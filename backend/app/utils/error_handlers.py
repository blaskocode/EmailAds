"""
Global error handlers and custom exception classes
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from typing import Union

logger = logging.getLogger(__name__)


class CampaignNotFoundError(Exception):
    """Raised when campaign is not found"""
    pass


class CampaignStateError(Exception):
    """Raised when campaign is in invalid state for operation"""
    pass


class S3Error(Exception):
    """Raised when S3 operation fails"""
    pass


class AIProcessingError(Exception):
    """Raised when AI processing fails"""
    pass


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with user-friendly messages"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with user-friendly messages"""
    errors = exc.errors()
    error_messages = []
    
    for error in errors:
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        error_messages.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "Validation failed",
            "details": error_messages,
            "status_code": 422
        }
    )


async def campaign_not_found_handler(request: Request, exc: CampaignNotFoundError):
    """Handle campaign not found errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": True,
            "message": str(exc) or "Campaign not found",
            "status_code": 404
        }
    )


async def campaign_state_error_handler(request: Request, exc: CampaignStateError):
    """Handle campaign state errors"""
    return JSONResponse(
        status_code=400,
        content={
            "error": True,
            "message": str(exc) or "Invalid campaign state for this operation",
            "status_code": 400
        }
    )


async def s3_error_handler(request: Request, exc: S3Error):
    """Handle S3 errors"""
    logger.error(f"S3 error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=503,
        content={
            "error": True,
            "message": "File storage service unavailable. Please try again later.",
            "status_code": 503
        }
    )


async def ai_processing_error_handler(request: Request, exc: AIProcessingError):
    """Handle AI processing errors"""
    logger.error(f"AI processing error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=502,
        content={
            "error": True,
            "message": "AI processing service unavailable. Please try again later.",
            "status_code": 502
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True, extra={
        "path": request.url.path,
        "method": request.method
    })
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "An unexpected error occurred. Please try again later.",
            "status_code": 500
        }
    )

