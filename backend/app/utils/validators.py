"""
File validation utilities
"""
from fastapi import UploadFile, HTTPException
from typing import List
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Allowed image MIME types
ALLOWED_IMAGE_TYPES = {
    'image/png',
    'image/jpeg',
    'image/jpg',
    'image/gif',  # Optional, but common
}

# Allowed image extensions
ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}

# Max file size (5MB in bytes)
MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE


def validate_image_file(file: UploadFile) -> None:
    """
    Validate that uploaded file is a valid image
    
    Args:
        file: UploadFile object
        
    Raises:
        HTTPException if file is invalid
    """
    # Check file size
    if hasattr(file, 'size') and file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File {file.filename} exceeds maximum size of {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
        )
    
    # Check content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File {file.filename} has invalid type {file.content_type}. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # Check file extension
    if file.filename:
        file_ext = '.' + file.filename.rsplit('.', 1)[-1].lower()
        if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} has invalid extension. Allowed extensions: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
            )


def validate_file_size(file_content: bytes) -> None:
    """
    Validate file size from content
    
    Args:
        file_content: File content as bytes
        
    Raises:
        HTTPException if file is too large
    """
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
        )


def validate_required_fields(data: dict, required_fields: List[str]) -> None:
    """
    Validate that required fields are present
    
    Args:
        data: Dictionary of form data
        required_fields: List of required field names
        
    Raises:
        HTTPException if required fields are missing
    """
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    import re
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    # Remove special characters except dots, dashes, underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    return filename

