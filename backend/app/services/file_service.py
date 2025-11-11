"""
File service for handling file uploads and processing
"""
from fastapi import UploadFile
from typing import List, Tuple
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


async def read_file_content(file: UploadFile) -> bytes:
    """
    Read file content into memory
    
    Args:
        file: UploadFile object
        
    Returns:
        File content as bytes
    """
    content = await file.read()
    # Reset file pointer for potential reuse
    await file.seek(0)
    return content


async def process_uploaded_files(
    logo: UploadFile,
    hero_images: List[UploadFile]
) -> Tuple[bytes, List[bytes]]:
    """
    Process uploaded files and return their content
    
    Args:
        logo: Logo file
        hero_images: List of hero image files
        
    Returns:
        Tuple of (logo_content, list of hero_image_contents)
    """
    # Read logo
    logo_content = await read_file_content(logo)
    
    # Read hero images
    hero_contents = []
    for hero_img in hero_images:
        content = await read_file_content(hero_img)
        hero_contents.append(content)
    
    return logo_content, hero_contents


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    
    Args:
        filename: File name
        
    Returns:
        File extension (e.g., '.png')
    """
    if not filename:
        return ''
    parts = filename.rsplit('.', 1)
    return '.' + parts[-1].lower() if len(parts) > 1 else ''


def generate_s3_key(campaign_id: str, filename: str, file_type: str = 'assets') -> str:
    """
    Generate S3 object key for file storage
    
    Args:
        campaign_id: Campaign ID
        filename: Original filename
        file_type: Type of file ('assets', 'proofs', 'html')
        
    Returns:
        S3 object key (path)
    """
    from app.utils.validators import sanitize_filename
    safe_filename = sanitize_filename(filename)
    return f"{file_type}/{campaign_id}/{safe_filename}"

