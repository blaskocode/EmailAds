"""
Image utility functions for processing and optimization
"""
from PIL import Image
from io import BytesIO
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Target sizes for email-safe images
LOGO_MAX_SIZE = (300, 100)  # width, height
HERO_MAX_SIZE = (600, 400)
TARGET_FILE_SIZE = 150 * 1024  # 150KB in bytes


def resize_image(
    image_bytes: bytes,
    max_size: Tuple[int, int],
    maintain_aspect: bool = True
) -> bytes:
    """
    Resize image to fit within max dimensions
    
    Args:
        image_bytes: Original image as bytes
        max_size: Maximum (width, height)
        maintain_aspect: Whether to maintain aspect ratio
        
    Returns:
        Resized image as bytes
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        original_format = img.format or 'JPEG'
        
        # Calculate new size
        if maintain_aspect:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        else:
            img = img.resize(max_size, Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary (for JPEG)
        if original_format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Save to bytes with optimization
        output = BytesIO()
        save_kwargs = {
            'format': original_format or 'JPEG',
            'optimize': True,
            'quality': 85
        }
        
        # Adjust quality to meet file size target
        for quality in [85, 75, 65, 55]:
            output.seek(0)
            output.truncate(0)
            save_kwargs['quality'] = quality
            img.save(output, **save_kwargs)
            
            if len(output.getvalue()) <= TARGET_FILE_SIZE:
                break
        
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        # Return original if resize fails
        return image_bytes


def get_image_dimensions(image_bytes: bytes) -> Tuple[int, int]:
    """
    Get image dimensions
    
    Args:
        image_bytes: Image as bytes
        
    Returns:
        (width, height) tuple
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        return img.size
    except Exception as e:
        logger.error(f"Error getting image dimensions: {e}")
        return (0, 0)


def convert_to_base64(image_bytes: bytes) -> str:
    """
    Convert image bytes to base64 string for API
    
    Args:
        image_bytes: Image as bytes
        
    Returns:
        Base64 encoded string
    """
    import base64
    return base64.b64encode(image_bytes).decode('utf-8')


def prepare_image_for_vision_api(image_bytes: bytes, max_dimension: int = 512) -> bytes:
    """
    Downscale image for GPT-4 Vision API (max 512px dimension)
    
    Args:
        image_bytes: Original image as bytes
        max_dimension: Maximum dimension (width or height)
        
    Returns:
        Downscaled image as bytes
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        width, height = img.size
        
        # Check if downscaling needed
        if max(width, height) <= max_dimension:
            return image_bytes
        
        # Calculate new size maintaining aspect ratio
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        output = BytesIO()
        img.save(output, format='JPEG', quality=85)
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Error preparing image for vision API: {e}")
        return image_bytes

