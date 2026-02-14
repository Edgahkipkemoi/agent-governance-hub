# Agent Audit System - FastAPI Backend
# Main application entry point

import os
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from services.agent_service import AgentService
from services.database_service import DatabaseService
from utils.risk_calculator import calculate_risk_status

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate required environment variables at startup
required_env_vars = [
    "GROQ_API_KEY",
    "GEMINI_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "FRONTEND_URL"
]

missing_vars = [var for var in required_env_vars if not os.getenv(var) or not os.getenv(var).strip()]
if missing_vars:
    error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
    logger.error(error_msg)
    raise ValueError(error_msg)

# Initialize FastAPI app
app = FastAPI(
    title="Agent Audit System",
    description="Real-time governance dashboard for AI agent monitoring",
    version="1.0.0"
)

# Configure CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    agent_service = AgentService()
    database_service = DatabaseService()
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {e}")
    raise


# Request/Response models
class ProcessAgentRequest(BaseModel):
    """Request model for processing agent queries."""
    user_query: str = Field(..., min_length=1, description="The user query to process")


class ProcessAgentResponse(BaseModel):
    """Response model for agent processing results."""
    id: str
    query: str
    response: str
    audit: Dict[str, Any]
    status: str
    created_at: str


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and their outcomes."""
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} - Error: {e}")
        raise


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Agent Audit System"}


@app.post("/process-agent", response_model=ProcessAgentResponse)
async def process_agent(request: ProcessAgentRequest):
    """
    Process a user query through the worker agent and audit the response.
    
    This endpoint:
    1. Validates the user query
    2. Sends it to the worker agent (Groq Llama 3)
    3. Audits the response with the auditor agent (Gemini)
    4. Calculates risk status
    5. Stores the audit log in the database
    6. Returns the complete audit log
    
    Args:
        request: ProcessAgentRequest containing the user_query
        
    Returns:
        ProcessAgentResponse with complete audit log
        
    Raises:
        HTTPException: For various error conditions (400, 500)
    """
    try:
        # Validate query
        if not request.user_query or not request.user_query.strip():
            logger.warning("Received empty query")
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Processing query: {request.user_query[:100]}...")
        
        # Step 1: Process query with worker agent
        try:
            worker_response = await agent_service.process_worker_query(request.user_query)
            logger.info("Worker agent processing completed")
        except Exception as e:
            logger.error(f"Worker agent failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Worker agent failed to process query: {str(e)}"
            )
        
        # Step 2: Audit the response
        try:
            audit_result = await agent_service.audit_response(
                request.user_query,
                worker_response.content
            )
            logger.info("Audit completed")
        except Exception as e:
            logger.warning(f"Auditor agent failed: {e}")
            # Fallback to default "Warning" status if auditor fails
            class FallbackAuditResult:
                def __init__(self):
                    self.risk_score = 5
                    self.hallucination_detected = False
                    self.pii_detected = False
                    self.toxic_content_detected = False
                    self.details = f"Audit failed: {str(e)}"
                
                def to_dict(self):
                    return {
                        'risk_score': self.risk_score,
                        'hallucination_detected': self.hallucination_detected,
                        'pii_detected': self.pii_detected,
                        'toxic_content_detected': self.toxic_content_detected,
                        'details': self.details
                    }
            
            audit_result = FallbackAuditResult()
        
        # Step 3: Calculate risk status
        risk_status = calculate_risk_status(audit_result.risk_score)
        logger.info(f"Risk status: {risk_status} (score: {audit_result.risk_score})")
        
        # Step 4: Store audit log in database
        try:
            log_id = await database_service.create_audit_log(
                query=request.user_query,
                response=worker_response.content,
                audit=audit_result.to_dict(),
                status=risk_status
            )
            logger.info(f"Audit log stored with ID: {log_id}")
        except Exception as e:
            logger.error(f"Database storage failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store audit log: {str(e)}"
            )
        
        # Step 5: Retrieve the created log to get timestamp
        try:
            logs = await database_service.get_recent_logs(limit=1)
            if logs and len(logs) > 0:
                created_log = logs[0]
                return ProcessAgentResponse(
                    id=created_log["id"],
                    query=created_log["query"],
                    response=created_log["response"],
                    audit=created_log["audit"],
                    status=created_log["status"],
                    created_at=created_log["created_at"]
                )
            else:
                raise Exception("Failed to retrieve created log")
        except Exception as e:
            logger.error(f"Failed to retrieve created log: {e}")
            # Return response without timestamp as fallback
            from datetime import datetime
            return ProcessAgentResponse(
                id=log_id,
                query=request.user_query,
                response=worker_response.content,
                audit=audit_result.to_dict(),
                status=risk_status,
                created_at=datetime.utcnow().isoformat()
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_agent: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )
