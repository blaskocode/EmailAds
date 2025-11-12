"""
Edit endpoints for campaign content and images
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional
import logging

from app.models.schemas import (
    CampaignEditRequest,
    CampaignEditResponse,
    ImageReplaceResponse
)
from app.services.campaign_service import get_campaign, update_campaign_content
from app.services.file_service import generate_s3_key, read_file_content, get_file_extension
from app.services.s3_service import s3_service
from app.utils.image_utils import resize_image, LOGO_MAX_SIZE, HERO_MAX_SIZE
from app.utils.validators import validate_image_file
from app.database import get_db
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/campaigns/{campaign_id}/edit", response_model=CampaignEditResponse)
async def edit_campaign_content(
    campaign_id: str,
    edit_request: CampaignEditRequest,
    conn = Depends(get_db)
):
    """
    Edit text content fields of a campaign
    
    This endpoint allows partial updates to text fields without re-processing images.
    Updates are applied to the ai_processing_data.content section.
    
    Args:
        campaign_id: Campaign ID to edit
        edit_request: Fields to update (all optional)
        
    Returns:
        Updated campaign data
    """
    try:
        # Get campaign
        campaign = await get_campaign(campaign_id, conn=conn)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Only allow editing campaigns that are ready or processed
        if campaign.status not in ['ready', 'processed', 'uploaded']:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot edit campaign with status '{campaign.status}'. "
                       f"Campaign must be in 'ready', 'processed', or 'uploaded' status."
            )
        
        # Update campaign content
        updated_campaign = await update_campaign_content(
            campaign_id,
            edit_request,
            conn=conn
        )
        
        if not updated_campaign:
            raise HTTPException(status_code=500, detail="Failed to update campaign")
        
        # Clear proof since content changed
        await updated_campaign.update(
            conn,
            proof_s3_path=None,
            status='processed' if campaign.status == 'ready' else campaign.status
        )
        
        logger.info(f"Updated campaign {campaign_id} content fields")
        
        return CampaignEditResponse(
            campaign_id=campaign_id,
            message="Campaign content updated successfully",
            status=updated_campaign.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error editing campaign {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to edit campaign: {str(e)}"
        )


@router.post("/campaigns/{campaign_id}/replace-image", response_model=ImageReplaceResponse)
async def replace_campaign_image(
    campaign_id: str,
    image_type: str = Form(..., description="Type of image: 'logo' or 'hero_{index}' (e.g., 'hero_0')"),
    file: UploadFile = File(..., description="New image file"),
    conn = Depends(get_db)
):
    """
    Replace a single image in a campaign (logo or hero image)
    
    Args:
        campaign_id: Campaign ID
        image_type: Type of image - 'logo' or 'hero_{index}' (e.g., 'hero_0', 'hero_1')
        file: New image file to upload
        
    Returns:
        Updated campaign data with new image URL
    """
    try:
        # Validate image file
        validate_image_file(file)
        
        # Get campaign
        campaign = await get_campaign(campaign_id, conn=conn)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Only allow editing campaigns that are ready or processed
        if campaign.status not in ['ready', 'processed', 'uploaded']:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot replace image in campaign with status '{campaign.status}'. "
                       f"Campaign must be in 'ready', 'processed', or 'uploaded' status."
            )
        
        # Parse image type
        is_logo = image_type == 'logo'
        is_hero = image_type.startswith('hero_')
        
        if not is_logo and not is_hero:
            raise HTTPException(
                status_code=400,
                detail="image_type must be 'logo' or 'hero_{index}' (e.g., 'hero_0')"
            )
        
        hero_index = None
        if is_hero:
            try:
                hero_index = int(image_type.split('_')[1])
            except (IndexError, ValueError):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid hero image index. Use format 'hero_0', 'hero_1', etc."
                )
        
        # Read file content
        file_content = await read_file_content(file)
        
        # Optimize image based on type
        max_size = LOGO_MAX_SIZE if is_logo else HERO_MAX_SIZE
        optimized_content = resize_image(file_content, max_size)
        
        # Get image format
        try:
            img = Image.open(BytesIO(optimized_content))
            optimized_format = img.format.lower() if img.format else 'jpeg'
        except Exception:
            optimized_format = 'jpeg'
        
        # Generate S3 key
        file_ext = get_file_extension(file.filename) or f".{optimized_format}"
        filename = f"{image_type}{file_ext}"
        s3_key = generate_s3_key(campaign_id, filename, 'assets')
        
        # Upload to S3
        s3_url = await s3_service.upload_file(
            BytesIO(optimized_content),
            s3_key,
            content_type=f'image/{optimized_format or "jpeg"}'
        )
        
        # Update campaign ai_processing_data with new image URL
        ai_data = campaign.ai_processing_data or {}
        
        # Ensure ai_results structure exists
        if 'ai_results' not in ai_data:
            ai_data['ai_results'] = {}
        if 'optimized_images' not in ai_data['ai_results']:
            ai_data['ai_results']['optimized_images'] = {}
        
        if is_logo:
            # Update logo in both top-level and ai_results
            if 'logo' not in ai_data:
                ai_data['logo'] = {}
            ai_data['logo']['s3_url'] = s3_url
            ai_data['logo']['filename'] = filename
            
            # Update in ai_results.optimized_images (used by template service)
            ai_data['ai_results']['optimized_images']['logo'] = s3_url
        else:
            # Update hero image at specified index
            if 'hero_images' not in ai_data:
                ai_data['hero_images'] = []
            
            # Ensure list is long enough
            while len(ai_data['hero_images']) <= hero_index:
                ai_data['hero_images'].append({})
            
            ai_data['hero_images'][hero_index] = {
                's3_url': s3_url,
                'filename': filename,
                'index': hero_index
            }
            
            # Update in ai_results.optimized_images (used by template service)
            if 'hero_images' not in ai_data['ai_results']['optimized_images']:
                ai_data['ai_results']['optimized_images']['hero_images'] = []
            
            # Ensure hero_images list is long enough
            hero_urls = ai_data['ai_results']['optimized_images']['hero_images']
            while len(hero_urls) <= hero_index:
                hero_urls.append(None)
            
            hero_urls[hero_index] = s3_url
        
        # Update campaign
        await campaign.update(
            conn,
            ai_processing_data=ai_data,
            proof_s3_path=None,  # Clear proof since image changed
            status='processed' if campaign.status == 'ready' else campaign.status
        )
        
        logger.info(f"Replaced {image_type} for campaign {campaign_id}")
        
        return ImageReplaceResponse(
            campaign_id=campaign_id,
            image_type=image_type,
            image_url=s3_url,
            message=f"Image {image_type} replaced successfully",
            status=campaign.status
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error replacing image for campaign {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to replace image: {str(e)}"
        )

