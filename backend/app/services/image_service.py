"""
Image service for optimization and processing
"""
from typing import List, Tuple, Optional
from io import BytesIO
import logging
from app.utils.image_utils import resize_image, LOGO_MAX_SIZE, HERO_MAX_SIZE
from app.services.s3_service import s3_service
from app.services.file_service import generate_s3_key

logger = logging.getLogger(__name__)


async def optimize_and_upload_logo(
    logo_bytes: bytes,
    campaign_id: str,
    original_filename: str
) -> Tuple[bytes, str]:
    """
    Optimize logo and upload to S3
    
    Args:
        logo_bytes: Original logo bytes
        campaign_id: Campaign ID
        original_filename: Original filename
        
    Returns:
        Tuple of (optimized_bytes, s3_url)
    """
    try:
        # Resize logo
        optimized_bytes = resize_image(logo_bytes, LOGO_MAX_SIZE)
        
        # Upload to S3
        s3_key = generate_s3_key(campaign_id, f"logo_optimized_{original_filename}", 'assets')
        logo_file_obj = BytesIO(optimized_bytes)
        s3_url = await s3_service.upload_file(
            logo_file_obj,
            s3_key,
            content_type='image/jpeg'
        )
        
        logger.info(f"Logo optimized and uploaded: {s3_url}")
        return optimized_bytes, s3_url
        
    except Exception as e:
        logger.error(f"Error optimizing logo: {e}")
        # Return original if optimization fails
        return logo_bytes, ""


async def optimize_and_upload_hero_images(
    hero_images_bytes: List[bytes],
    campaign_id: str,
    original_filenames: List[str]
) -> List[Tuple[bytes, str]]:
    """
    Optimize hero images and upload to S3
    
    Args:
        hero_images_bytes: List of hero image bytes
        campaign_id: Campaign ID
        original_filenames: List of original filenames
        
    Returns:
        List of tuples (optimized_bytes, s3_url)
    """
    results = []
    
    for idx, (hero_bytes, filename) in enumerate(zip(hero_images_bytes, original_filenames)):
        try:
            # Resize hero image
            optimized_bytes = resize_image(hero_bytes, HERO_MAX_SIZE)
            
            # Upload to S3
            s3_key = generate_s3_key(
                campaign_id,
                f"hero_{idx}_optimized_{filename}",
                'assets'
            )
            hero_file_obj = BytesIO(optimized_bytes)
            s3_url = await s3_service.upload_file(
                hero_file_obj,
                s3_key,
                content_type='image/jpeg'
            )
            
            logger.info(f"Hero image {idx} optimized and uploaded: {s3_url}")
            results.append((optimized_bytes, s3_url))
            
        except Exception as e:
            logger.error(f"Error optimizing hero image {idx}: {e}")
            # Use original if optimization fails
            results.append((hero_bytes, ""))
    
    return results


async def download_image_from_s3(s3_url: str) -> Optional[bytes]:
    """
    Download image from S3 URL (runs in thread pool)
    
    Args:
        s3_url: S3 URL (s3://bucket/key format)
        
    Returns:
        Image bytes or None if download fails
    """
    try:
        # Extract bucket and key from s3:// URL
        if not s3_url.startswith('s3://'):
            logger.error(f"Invalid S3 URL format: {s3_url}")
            return None
        
        parts = s3_url.replace('s3://', '').split('/', 1)
        if len(parts) != 2:
            logger.error(f"Invalid S3 URL format: {s3_url}")
            return None
        
        bucket_name, key = parts
        
        # Download from S3 using the existing s3_service
        # We need to use boto3 directly for downloads
        import boto3
        import asyncio
        from app.config import settings
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        # Download in thread pool
        def download():
            response = s3_client.get_object(Bucket=bucket_name, Key=key)
            return response['Body'].read()
        
        image_bytes = await asyncio.to_thread(download)
        logger.info(f"Downloaded image from S3: {key}")
        return image_bytes
        
    except Exception as e:
        logger.error(f"Error downloading image from S3: {e}")
        return None

