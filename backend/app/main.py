"""
HiBid Email MVP - FastAPI Application
Main entry point for the backend API
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.database import db
from app.services.s3_service import s3_service
from app.utils.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    campaign_not_found_handler,
    campaign_state_error_handler,
    s3_error_handler,
    ai_processing_error_handler,
    general_exception_handler,
    CampaignNotFoundError,
    CampaignStateError,
    S3Error,
    AIProcessingError
)
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting HiBid Email MVP API...")
    try:
        # Initialize database
        await db.init_db()
        logger.info("Database initialized")
        
        # Test S3 connection
        s3_connected = await s3_service.test_connection()
        if s3_connected:
            logger.info("S3 connection verified")
        else:
            logger.warning("S3 connection test failed - check credentials and bucket name")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down HiBid Email MVP API...")
    await db.close()


app = FastAPI(
    title="HiBid Email MVP API",
    description="Automated email advertising workflow system",
    version="1.0.0",
    lifespan=lifespan
)

# Register global exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(CampaignNotFoundError, campaign_not_found_handler)
app.add_exception_handler(CampaignStateError, campaign_state_error_handler)
app.add_exception_handler(S3Error, s3_error_handler)
app.add_exception_handler(AIProcessingError, ai_processing_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
from app.routes import upload, process, generate, preview, approve, download
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(process.router, prefix="/api/v1", tags=["process"])
app.include_router(generate.router, prefix="/api/v1", tags=["generate"])
app.include_router(preview.router, prefix="/api/v1", tags=["preview"])
app.include_router(approve.router, prefix="/api/v1", tags=["approve"])
app.include_router(download.router, prefix="/api/v1", tags=["download"])


@app.get("/health")
async def health_check():
    """Health check endpoint with database and S3 status"""
    health_status = {
        "status": "healthy",
        "service": "hibid-email-mvp",
        "database": "connected",
        "s3": "unknown"
    }
    
    # Test database connection
    try:
        await db.connect()
        await db.close()
        health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["database"] = "disconnected"
        health_status["status"] = "degraded"
    
    # Test S3 connection
    try:
        s3_connected = await s3_service.test_connection()
        health_status["s3"] = "connected" if s3_connected else "disconnected"
        if not s3_connected:
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"S3 health check failed: {e}")
        health_status["s3"] = "error"
        health_status["status"] = "degraded"
    
    return health_status


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HiBid Email MVP API",
        "version": "1.0.0",
        "docs": "/docs",
        "api_version": "v1",
        "api_base": "/api/v1"
    }

