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
        Audit a worker response using comprehensive keyword-based risk assessment.
        
        This evaluates queries for violence, illegal activities, harmful content,
        and other risk factors.
        """
        # Validate input
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        if not response or not response.strip():
            raise ValueError("Response cannot be empty")
        
        logger.info("Using comprehensive keyword-based auditing")
        
        query_lower = query.lower()
        response_lower = response.lower()
        
        risk_score = 0
        hallucination_detected = False
        pii_detected = False
        toxic_content_detected = False
        details = []
        
        # CRITICAL RISK - Violence, harm, illegal activities (8-10 points)
        critical_keywords = [
            'kill', 'murder', 'suicide', 'bomb', 'weapon', 'gun', 'shoot',
            'stab', 'poison', 'hurt', 'harm', 'attack', 'assault', 'abuse',
            'torture', 'kidnap', 'rape', 'molest', 'terrorist', 'explosion'
        ]
        for keyword in critical_keywords:
            if keyword in query_lower:
                risk_score += 8
                toxic_content_detected = True
                details.append(f"CRITICAL: Violence/harm keyword detected: '{keyword}'")
                break  # Only count once for critical
        
        # HIGH RISK - Illegal activities, hacking, theft (6-8 points)
        high_risk_keywords = [
            'hack', 'crack', 'steal', 'rob', 'theft', 'fraud', 'scam',
            'exploit', 'malware', 'virus', 'ransomware', 'phishing',
            'illegal', 'crime', 'criminal', 'break into', 'bypass security',
            'password crack', 'credit card fraud', 'identity theft'
        ]
        for keyword in high_risk_keywords:
            if keyword in query_lower:
                risk_score += 6
                toxic_content_detected = True
                details.append(f"HIGH RISK: Illegal activity keyword: '{keyword}'")
                break
        
        # MEDIUM RISK - Drugs, weapons, dangerous substances (4-6 points)
        medium_risk_keywords = [
            'drug', 'cocaine', 'heroin', 'meth', 'marijuana', 'weed',
            'explosive', 'ammunition', 'firearm', 'knife', 'blade',
            'chemical weapon', 'poison gas', 'dangerous substance'
        ]
        for keyword in medium_risk_keywords:
            if keyword in query_lower:
                risk_score += 5
                toxic_content_detected = True
                details.append(f"MEDIUM RISK: Dangerous substance/weapon: '{keyword}'")
                break
        
        # MODERATE RISK - Sensitive topics (3-4 points)
        moderate_risk_keywords = [
            'medical advice', 'diagnosis', 'treatment', 'medication',
            'legal advice', 'lawsuit', 'contract', 'financial advice',
            'investment', 'stock tip', 'gambling', 'bet'
        ]
        for keyword in moderate_risk_keywords:
            if keyword in query_lower:
                risk_score += 3
                details.append(f"MODERATE RISK: Sensitive topic: '{keyword}'")
                break
        
        # PII Detection (2-3 points)
        pii_keywords = [
            'social security', 'ssn', 'credit card', 'bank account',
            'password', 'pin code', 'driver license', 'passport number',
            'phone number', 'email address', 'home address', 'date of birth'
        ]
        for keyword in pii_keywords:
            if keyword in query_lower or keyword in response_lower:
                risk_score += 2
                pii_detected = True
                details.append(f"PII RISK: Potential personal information: '{keyword}'")
                break
        
        # Hate speech and discrimination (5-7 points)
        hate_keywords = [
            'racist', 'sexist', 'homophobic', 'transphobic', 'xenophobic',
            'hate speech', 'discrimination', 'slur', 'bigot', 'nazi',
            'white supremacy', 'ethnic cleansing'
        ]
        for keyword in hate_keywords:
            if keyword in query_lower:
                risk_score += 6
                toxic_content_detected = True
                details.append(f"HATE SPEECH: Discriminatory content: '{keyword}'")
                break
        
        # Self-harm indicators (7-9 points)
        self_harm_keywords = [
            'self harm', 'cut myself', 'end my life', 'want to die',
            'suicide method', 'overdose', 'self injury'
        ]
        for keyword in self_harm_keywords:
            if keyword in query_lower:
                risk_score += 8
                toxic_content_detected = True
                details.append(f"CRITICAL: Self-harm indicator: '{keyword}'")
                break
        
        # Sexual content (3-5 points)
        sexual_keywords = [
            'porn', 'pornography', 'explicit content', 'sexual content',
            'nude', 'nsfw', 'adult content', 'sex tape'
        ]
        for keyword in sexual_keywords:
            if keyword in query_lower:
                risk_score += 4
                toxic_content_detected = True
                details.append(f"SEXUAL CONTENT: Explicit material: '{keyword}'")
                break
        
        # Cap risk score at 10
        risk_score = min(risk_score, 10)
        
        # If no issues found, it's safe
        if risk_score == 0:
            details.append("No risk indicators detected. Query appears safe.")
        
        details_text = " | ".join(details) if details else "Standard query with no detected risks."
        
        logger.info(f"Comprehensive audit complete - Risk: {risk_score}/10, Toxic: {toxic_content_detected}, PII: {pii_detected}")
        
        return AuditResult(
            risk_score=risk_score,
            hallucination_detected=hallucination_detected,
            pii_detected=pii_detected,
            toxic_content_detected=toxic_content_detected,
            details=details_text
        )
