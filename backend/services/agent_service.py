"""
Agent Service

This module provides integration with AI agents for query processing and auditing.
It handles communication with Groq (worker agent) and includes retry logic with
exponential backoff for resilient API interactions.
"""

import os
import logging
import time
import json
from typing import Dict, Any, Optional
from groq import Groq
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class WorkerResponse:
    """Data model for worker agent responses."""
    
    def __init__(self, content: str, model: str, tokens_used: int):
        self.content = content
        self.model = model
        self.tokens_used = tokens_used


class AuditResult:
    """Data model for audit results."""
    
    def __init__(self, risk_score: int, hallucination_detected: bool, 
                 pii_detected: bool, toxic_content_detected: bool, details: str):
        self.risk_score = risk_score
        self.hallucination_detected = hallucination_detected
        self.pii_detected = pii_detected
        self.toxic_content_detected = toxic_content_detected
        self.details = details
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit result to dictionary."""
        return {
            "risk_score": self.risk_score,
            "hallucination_detected": self.hallucination_detected,
            "pii_detected": self.pii_detected,
            "toxic_content_detected": self.toxic_content_detected,
            "details": self.details
        }


class AgentService:
    """
    Service for managing AI agent interactions.
    
    This service handles communication with the Groq worker agent (Llama 3)
    and includes retry logic with exponential backoff for resilient operations.
    """
    
    def __init__(self):
        """
        Initialize the AgentService with Groq and Gemini clients.
        
        Raises:
            ValueError: If required environment variables are missing
            Exception: If client initialization fails
        """
        # Get environment variables
        groq_api_key = os.getenv("GROQ_API_KEY")
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Validate environment variables
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        try:
            # Initialize Groq client
            self.groq_client = Groq(api_key=groq_api_key)
            
            # Initialize Gemini client
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            logger.info("AgentService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize clients: {e}")
            raise Exception(f"Failed to initialize agent service: {e}")
    
    async def process_worker_query(self, query: str) -> WorkerResponse:
        """
        Send query to Groq Llama 3 worker agent and return response.
        
        This method implements retry logic with exponential backoff to handle
        transient failures. It will retry up to 3 times with delays of 1s, 2s, 4s.
        
        Args:
            query: The user query to process
            
        Returns:
            WorkerResponse containing the agent's response and metadata
            
        Raises:
            ValueError: If query is empty or invalid
            Exception: If all retry attempts fail
        """
        # Validate input
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        # Retry configuration
        max_attempts = 3
        base_delay = 1.0  # seconds
        
        last_exception = None
        
        for attempt in range(1, max_attempts + 1):
            try:
                # Log the request
                logger.info(f"Sending query to Groq worker agent (attempt {attempt}/{max_attempts})")
                logger.debug(f"Query: {query[:100]}...")  # Log first 100 chars
                
                # Call Groq API
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": query,
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                    max_tokens=1024,
                )
                
                # Extract response
                content = chat_completion.choices[0].message.content
                model = chat_completion.model
                tokens_used = chat_completion.usage.total_tokens
                
                # Log the response
                logger.info(f"Received response from Groq worker agent")
                logger.debug(f"Response: {content[:100]}...")  # Log first 100 chars
                logger.info(f"Tokens used: {tokens_used}, Model: {model}")
                
                # Return successful response
                return WorkerResponse(
                    content=content,
                    model=model,
                    tokens_used=tokens_used
                )
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Groq API call failed (attempt {attempt}/{max_attempts}): {e}")
                
                # If this was the last attempt, don't sleep
                if attempt == max_attempts:
                    break
                
                # Calculate exponential backoff delay
                delay = base_delay * (2 ** (attempt - 1))
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
        
        # All attempts failed
        error_msg = f"Worker agent failed after {max_attempts} attempts: {last_exception}"
        logger.error(error_msg)
        raise Exception(error_msg)

    async def audit_response(self, query: str, response: str) -> AuditResult:
        """
        Audit a worker response using Google Gemini for risk assessment.
        
        TEMPORARY: Using simple keyword-based auditing due to Gemini API issues.
        This will be replaced with actual Gemini auditing once API access is restored.
        """
        # Validate input
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        if not response or not response.strip():
            raise ValueError("Response cannot be empty")
        
        logger.info("Using keyword-based auditing (Gemini API unavailable)")
        
        # Simple keyword-based risk assessment
        query_lower = query.lower()
        response_lower = response.lower()
        
        risk_score = 0
        hallucination_detected = False
        pii_detected = False
        toxic_content_detected = False
        details = []
        
        # Check for high-risk keywords
        high_risk_keywords = ['hack', 'password', 'crack', 'exploit', 'malware', 'virus', 'illegal']
        for keyword in high_risk_keywords:
            if keyword in query_lower:
                risk_score += 3
                toxic_content_detected = True
                details.append(f"High-risk keyword detected: '{keyword}'")
        
        # Check for PII patterns
        pii_keywords = ['email', 'phone', 'address', 'ssn', 'credit card', 'personal']
        for keyword in pii_keywords:
            if keyword in query_lower or keyword in response_lower:
                risk_score += 2
                pii_detected = True
                details.append(f"Potential PII reference: '{keyword}'")
        
        # Check for medical/legal advice
        sensitive_topics = ['medical', 'legal', 'financial advice', 'diagnosis', 'treatment']
        for topic in sensitive_topics:
            if topic in query_lower:
                risk_score += 1
                details.append(f"Sensitive topic: '{topic}'")
        
        # Cap risk score at 10
        risk_score = min(risk_score, 10)
        
        # If no issues found, it's safe
        if risk_score == 0:
            details.append("No risk indicators detected. Query appears safe.")
        
        details_text = " | ".join(details) if details else "Standard query with no detected risks."
        
        logger.info(f"Keyword-based audit complete - Risk: {risk_score}/10")
        
        return AuditResult(
            risk_score=risk_score,
            hallucination_detected=hallucination_detected,
            pii_detected=pii_detected,
            toxic_content_detected=toxic_content_detected,
            details=details_text
        )
