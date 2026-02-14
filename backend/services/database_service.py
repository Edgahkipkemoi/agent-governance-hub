"""
Database Service

This module provides database operations for storing and retrieving audit logs
using Supabase as the backend database.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Service for managing audit log persistence in Supabase.
    
    This service handles all database operations including creating audit logs
    and retrieving recent logs with proper error handling.
    """
    
    def __init__(self):
        """
        Initialize the DatabaseService with Supabase client.
        
        Raises:
            ValueError: If required environment variables are missing
            Exception: If Supabase client initialization fails
        """
        # Get environment variables
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        # Validate environment variables
        if not supabase_url:
            raise ValueError("SUPABASE_URL environment variable is required")
        if not supabase_key:
            raise ValueError("SUPABASE_SERVICE_ROLE_KEY environment variable is required")
        
        try:
            # Initialize Supabase client
            self.client: Client = create_client(supabase_url, supabase_key)
            logger.info("DatabaseService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise Exception(f"Failed to initialize database connection: {e}")
    
    async def create_audit_log(
        self,
        query: str,
        response: str,
        audit: Dict[str, Any],
        status: str
    ) -> str:
        """
        Create a new audit log entry in the database.
        
        Args:
            query: The user query that was processed
            response: The worker agent's response
            audit: Dictionary containing audit results (risk_score, flags, details, etc.)
            status: Risk status classification ("Safe", "Warning", or "Flagged")
            
        Returns:
            UUID string of the created log entry
            
        Raises:
            ValueError: If required fields are empty or invalid
            Exception: If database insertion fails
        """
        # Validate inputs
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        if not response or not response.strip():
            raise ValueError("Response cannot be empty")
        if not audit:
            raise ValueError("Audit data cannot be empty")
        if status not in ["Safe", "Warning", "Flagged"]:
            raise ValueError(f"Invalid status: {status}. Must be Safe, Warning, or Flagged")
        
        # Validate audit structure
        required_audit_fields = ["risk_score", "hallucination_detected", "pii_detected", "toxic_content_detected"]
        for field in required_audit_fields:
            if field not in audit:
                raise ValueError(f"Audit data missing required field: {field}")
        
        try:
            # Insert log into database
            result = self.client.table("logs").insert({
                "query": query,
                "response": response,
                "audit": audit,
                "status": status
            }).execute()
            
            # Extract the UUID from the result
            if result.data and len(result.data) > 0:
                log_id = result.data[0]["id"]
                logger.info(f"Created audit log with ID: {log_id}")
                return log_id
            else:
                raise Exception("Database insert succeeded but no ID was returned")
                
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            raise Exception(f"Database error: Failed to create audit log - {e}")
    
    async def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve recent audit logs from the database.
        
        Args:
            limit: Maximum number of logs to retrieve (default: 50)
            
        Returns:
            List of audit log dictionaries, ordered by created_at descending
            
        Raises:
            ValueError: If limit is invalid
            Exception: If database query fails
        """
        # Validate limit
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError(f"Limit must be a positive integer, got: {limit}")
        
        try:
            # Query logs from database
            result = self.client.table("logs")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            logs = result.data if result.data else []
            logger.info(f"Retrieved {len(logs)} audit logs")
            return logs
            
        except Exception as e:
            logger.error(f"Failed to retrieve audit logs: {e}")
            raise Exception(f"Database error: Failed to retrieve audit logs - {e}")
