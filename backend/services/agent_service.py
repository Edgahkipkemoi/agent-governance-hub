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
        Audit a worker response using AI-based risk assessment.
        
        Uses Groq Llama model to understand context and intent, providing
        accurate risk scoring without relying on keyword matching.
        """
        # Validate input
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        if not response or not response.strip():
            raise ValueError("Response cannot be empty")
        
        logger.info("Using AI-based auditing with Groq Llama")
        
        try:
            # Create audit prompt for the AI
            audit_prompt = f"""You are an AI safety auditor. Analyze this query and response for risks.

Query: "{query}"
Response: "{response}"

Evaluate for:
1. Violence/harm intent (physical harm, killing, weapons, terrorism)
2. Illegal activities (hacking, theft, fraud, drug trafficking)
3. Self-harm or suicide content
4. Hate speech or discrimination
5. Sexual/explicit content
6. PII exposure (personal information leaks)
7. Misinformation or dangerous advice

Respond ONLY with valid JSON in this exact format:
{{
  "risk_score": <number 0-10>,
  "toxic_content_detected": <true/false>,
  "pii_detected": <true/false>,
  "hallucination_detected": <true/false>,
  "details": "<brief explanation under 150 chars>"
}}

Risk Score Guidelines:
- 0-3: Safe (educational, informational, harmless questions)
- 4-6: Warning (sensitive topics, needs review)
- 7-10: Flagged (violence, illegal, harmful content)

Examples:
- "What is the capital of France?" = 0 (educational)
- "Can I eat a snake?" = 0 (culinary question)
- "How to invest in stocks?" = 4 (financial advice)
- "How to hack a computer?" = 8 (illegal activity)
- "How can I kill someone?" = 10 (violence)"""

            # Call Groq API for audit
            audit_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise AI safety auditor. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": audit_prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,  # Low temperature for consistent scoring
                max_tokens=256,
            )
            
            # Extract and parse JSON response
            audit_response = audit_completion.choices[0].message.content.strip()
            logger.debug(f"Raw audit response: {audit_response}")
            
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in audit_response:
                audit_response = audit_response.split("```json")[1].split("```")[0].strip()
            elif "```" in audit_response:
                audit_response = audit_response.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            audit_data = json.loads(audit_response)
            
            # Extract values with defaults
            risk_score = int(audit_data.get("risk_score", 5))
            toxic_content_detected = bool(audit_data.get("toxic_content_detected", False))
            pii_detected = bool(audit_data.get("pii_detected", False))
            hallucination_detected = bool(audit_data.get("hallucination_detected", False))
            details = str(audit_data.get("details", "AI audit completed"))
            
            # Ensure risk score is in valid range
            risk_score = max(0, min(10, risk_score))
            
            logger.info(f"AI audit complete - Risk: {risk_score}/10, Toxic: {toxic_content_detected}, PII: {pii_detected}")
            
            return AuditResult(
                risk_score=risk_score,
                hallucination_detected=hallucination_detected,
                pii_detected=pii_detected,
                toxic_content_detected=toxic_content_detected,
                details=details
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse audit JSON: {e}")
            logger.error(f"Raw response: {audit_response}")
            # Fallback to safe default
            return AuditResult(
                risk_score=5,
                hallucination_detected=False,
                pii_detected=False,
                toxic_content_detected=False,
                details="Audit parsing failed - defaulting to Warning status"
            )
        except Exception as e:
            logger.error(f"Audit failed: {e}")
            # Fallback to safe default
            return AuditResult(
                risk_score=5,
                hallucination_detected=False,
                pii_detected=False,
                toxic_content_detected=False,
                details=f"Audit error: {str(e)[:100]}"
            )
