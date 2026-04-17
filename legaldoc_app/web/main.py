from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field, validator
import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import json
import re
import hashlib
import time
from datetime import datetime
from uuid import uuid4
from typing import Optional, List
import unicodedata
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pythonjsonlogger import jsonlogger

# Load environment variables
load_dotenv()

# Configure structured logging
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

# Initialize FastAPI app
app = FastAPI(
    title="LegalDoc API",
    description="AI-powered legal document simplification API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter

# Configure CORS with environment-based origins
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:8000"
).split(",")

ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)

# Configure Google Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    logger.error("GEMINI_API_KEY environment variable not set")
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=gemini_api_key)

# Configuration
MAX_DOCUMENT_SIZE_MB = int(os.getenv("MAX_DOCUMENT_SIZE_MB", "50"))
MAX_QUESTION_LENGTH = 500
MIN_QUESTION_LENGTH = 1
MAX_DOCUMENT_LENGTH = 100000

# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for document analysis"""
    question: str = Field(
        ...,
        min_length=MIN_QUESTION_LENGTH,
        max_length=MAX_QUESTION_LENGTH,
        description="Question about the legal document"
    )
    document: str = Field(
        ...,
        min_length=1,
        max_length=MAX_DOCUMENT_LENGTH,
        description="Legal document text to analyze"
    )
    
    @validator('question', 'document', pre=True)
    def sanitize_input(cls, v):
        """Sanitize input to prevent injection attacks"""
        if not isinstance(v, str):
            raise ValueError("Input must be a string")
        # Remove control characters
        v = "".join(ch for ch in v if unicodedata.category(ch)[0] != "C")
        # Normalize unicode
        v = unicodedata.normalize("NFKC", v).strip()
        return v


class DocumentAnalysis(BaseModel):
    """Response model for document analysis"""
    analysis_id: str
    response: str
    document_hash: str
    question_length: int
    document_length: int
    processing_time_ms: float
    timestamp: str
    api_version: str = "1.0.0"


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str = "1.0.0"


# Helper functions
def sanitize_text(text: str) -> str:
    """Remove control characters and normalize unicode"""
    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C")
    return unicodedata.normalize("NFKC", text)


def hash_document(document: str) -> str:
    """Create a hash of the document for tracking""" 
    return hashlib.sha256(document.encode()).hexdigest()[:16]


def simplify_with_gemini(document_text: str, question: str, analysis_id: str) -> str:
    """Use Google Gemini to simplify the legal document""" 
    try:
        logger.info(
            "gemini_request_started",
            extra={
                "analysis_id": analysis_id,
                "doc_length": len(document_text),
                "question_length": len(question)
            }
        )
        
        # List of Gemini models to try
        model_names = [
            "gemini-1.5-pro",
            "gemini-1.0-pro",
            "gemini-pro",
        ]
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                prompt = f"""You are a legal expert who simplifies complex legal documents into plain English.

Question: {question}

Please analyze the following legal document and provide a clear, easy-to-understand explanation.

Document:
{document_text}

Provide a simplified explanation that covers:
1. The main purpose of the document
2. Key terms and what they mean in plain language
3. Important obligations or rights mentioned
4. Any potential risks or considerations
5. Overall summary

Write in a friendly, accessible tone suitable for someone without legal training.
Keep your response under 500 words."""

                response = model.generate_content(prompt)
                
                logger.info(
                    "gemini_request_completed",
                    extra={"analysis_id": analysis_id, "model": model_name}
                )
                
                return response.text
                
            except Exception as e:
                logger.warning(
                    f"gemini_model_failed",
                    extra={
                        "analysis_id": analysis_id,
                        "model": model_name,
                        "error": str(e)
                    }
                )
                continue
        
        raise Exception("All Gemini model attempts failed")
        
    except Exception as e:
        logger.error(
            "gemini_api_error",
            extra={"analysis_id": analysis_id, "error": str(e)}
        )
        raise Exception(f"Gemini API error: {str(e)}")


# Endpoints
@app.get("/health", response_model=HealthCheck)
@limiter.limit("1000/minute")
async def health_check(request: Request):
    """Health check endpoint""" 
    logger.info("health_check_called")
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.post("/chat", response_model=DocumentAnalysis)
@limiter.limit("100/minute")
async def chat_endpoint(request: Request, chat_request: ChatRequest):
    """
    Analyze a legal document and provide simplified explanation
    
    - **question**: User's question about the document (1-500 chars)
    - **document**: Legal document text to analyze (1-100k chars)
    """
    analysis_id = str(uuid4())
    start_time = time.time()
    
    try:
        # Validate document size
        doc_size_mb = len(chat_request.document.encode('utf-8')) / (1024 * 1024)
        if doc_size_mb > MAX_DOCUMENT_SIZE_MB:
            logger.warning(
                "document_size_exceeded",
                extra={"analysis_id": analysis_id, "size_mb": doc_size_mb}
            )
            raise HTTPException(
                status_code=413,
                detail=f"Document too large. Maximum size: {MAX_DOCUMENT_SIZE_MB}MB"
            )
        
        logger.info(
            "chat_request_received",
            extra={
                "analysis_id": analysis_id,
                "client_ip": request.client.host if request.client else "unknown",
                "doc_length": len(chat_request.document),
                "question_length": len(chat_request.question)
            }
        )
        
        # Sanitize inputs
        document_text = sanitize_text(chat_request.document)
        question = sanitize_text(chat_request.question)
        document_hash = hash_document(document_text)
        
        # Use Google Gemini for simplification
        simplified_text = simplify_with_gemini(document_text, question, analysis_id)
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        logger.info(
            "chat_request_completed",
            extra={
                "analysis_id": analysis_id,
                "processing_time_ms": processing_time,
                "response_length": len(simplified_text)
            }
        )
        
        return DocumentAnalysis(
            analysis_id=analysis_id,
            response=simplified_text,
            document_hash=document_hash,
            question_length=len(question),
            document_length=len(document_text),
            processing_time_ms=round(processing_time, 2),
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "chat_request_error",
            extra={"analysis_id": analysis_id, "error": str(e)},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Error processing request. Please try again or contact support."
        )


@app.get("/", response_class=HTMLResponse)
@limiter.limit("100/minute")
async def read_root(request: Request):
    """Serve the main HTML UI""" 
    try:
        with open("index.html", "r") as f:
            html_content = f.read()
        return html_content
    except FileNotFoundError:
        logger.warning("index.html not found, serving default UI")
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>LegalDoc - Legal Document Simplifier</title>
        </head>
        <body>
            <h1>LegalDoc API</h1>
            <p>Legal Document Simplification API is running.</p>
            <p>API Documentation: <a href="/docs">/docs</a></p>
            <p>Use the /chat endpoint to simplify legal documents.</p>
        </body>
        </html>
        """
        return html_content


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors""" 
    logger.warning(
        "rate_limit_exceeded",
        extra={"client_ip": request.client.host if request.client else "unknown"}
    )
    return {
        "detail": "Rate limit exceeded. Maximum 100 requests per minute allowed.",
        "retry_after": 60
    }


# Log startup
logger.info("legaldoc_api_startup", extra={
    "version": "1.0.0",
    "cors_origins": ALLOWED_ORIGINS,
    "max_document_size_mb": MAX_DOCUMENT_SIZE_MB
})
