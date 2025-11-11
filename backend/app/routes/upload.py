"""
Upload endpoint for campaign asset uploads
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List, Optional
from io import BytesIO
import logging

from app.models.schemas import CampaignCreateRequest, CampaignUploadResponse
from app.services.file_service import process_uploaded_files, generate_s3_key
from app.services.campaign_service import create_campaign, update_campaign_assets
from app.services.s3_service import s3_service
from app.utils.validators import (
    validate_image_file,
    validate_file_size,
    validate_required_fields
)
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=CampaignUploadResponse)
async def upload_campaign(
    campaign_name: str = Form(..., min_length=1, max_length=200),
    advertiser_name: str = Form(..., min_length=1, max_length=200),
    logo: UploadFile = File(..., description="Logo image file"),
    hero_images: List[UploadFile] = File(default=[], description="Hero image files (1-3)"),
    subject_line: Optional[str] = Form(None, max_length=200),
    preview_text: Optional[str] = Form(None, max_length=200),
    body_copy: Optional[str] = Form(None, max_length=5000),
    cta_text: Optional[str] = Form(None, max_length=50),
    cta_url: Optional[str] = Form(None, max_length=500),
    footer_text: Optional[str] = Form(None, max_length=500),
    conn = Depends(get_db)
):
    """
    Upload campaign assets and create campaign record
    
    Accepts:
    - Logo (required): Single image file
    - Hero images (optional): 1-3 image files
    - Text content: Campaign metadata
    
    Returns:
    - campaign_id: UUID for the created campaign
    - status: Current campaign status
    """
    try:
        # Validate required fields
        validate_required_fields(
            {'campaign_name': campaign_name, 'advertiser_name': advertiser_name},
            ['campaign_name', 'advertiser_name']
        )
        
        # Validate logo file
        if not logo.filename:
            raise HTTPException(
                status_code=400,
                detail="Logo file is required"
            )
        validate_image_file(logo)
        logo_content = await logo.read()
        if not logo_content:
            raise HTTPException(
                status_code=400,
                detail="Logo file is empty"
            )
        validate_file_size(logo_content)
        
        # Validate hero images (1-3 files)
        if len(hero_images) > 3:
            raise HTTPException(
                status_code=400,
                detail="Maximum 3 hero images allowed"
            )
        
        hero_contents = []
        for hero_img in hero_images:
            if not hero_img.filename:
                continue  # Skip empty file entries
            validate_image_file(hero_img)
            hero_content = await hero_img.read()
            if hero_content:
                validate_file_size(hero_content)
                hero_contents.append((hero_img, hero_content))
        
        # Create campaign record first
        try:
            campaign = await create_campaign(
                campaign_name=campaign_name,
                advertiser_name=advertiser_name,
                conn=conn
            )
        except Exception as e:
            logger.error(f"Error creating campaign: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create campaign: {str(e)}"
            )
        
        # Upload logo to S3
        try:
            logo_s3_key = generate_s3_key(campaign.id, logo.filename, 'assets')
            logo_file_obj = BytesIO(logo_content)
            logo_s3_url = await s3_service.upload_file(
                logo_file_obj,
                logo_s3_key,
                content_type=logo.content_type or 'image/png'
            )
        except Exception as e:
            logger.error(f"Error uploading logo to S3: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload logo to S3: {str(e)}"
            )
        
        # Upload hero images to S3 and collect metadata
        hero_s3_urls = []
        hero_metadata = []
        for idx, (hero_img, hero_content) in enumerate(hero_contents):
            try:
                hero_s3_key = generate_s3_key(
                    campaign.id,
                    hero_img.filename or f"hero_{idx}.jpg",
                    'assets'
                )
                hero_file_obj = BytesIO(hero_content)
                hero_s3_url = await s3_service.upload_file(
                    hero_file_obj,
                    hero_s3_key,
                    content_type=hero_img.content_type or 'image/jpeg'
                )
                hero_s3_urls.append(hero_s3_url)
                hero_metadata.append({
                    'filename': hero_img.filename,
                    's3_key': hero_s3_key,
                    's3_url': hero_s3_url,
                    'content_type': hero_img.content_type or 'image/jpeg',
                    'size': len(hero_content)
                })
            except Exception as e:
                logger.error(f"Error uploading hero image {idx} to S3: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload hero image to S3: {str(e)}"
                )
        
        # Store asset metadata
        asset_metadata = {
            'logo': {
                'filename': logo.filename,
                's3_key': logo_s3_key,
                's3_url': logo_s3_url,
                'content_type': logo.content_type,
                'size': len(logo_content)
            },
            'hero_images': hero_metadata,
            'content': {
                'subject_line': subject_line,
                'preview_text': preview_text,
                'body_copy': body_copy,
                'cta_text': cta_text,
                'cta_url': cta_url,
                'footer_text': footer_text
            }
        }
        
        # Update campaign with S3 paths
        try:
            assets_s3_path = f"assets/{campaign.id}/"
            await update_campaign_assets(
                campaign.id,
                assets_s3_path,
                asset_metadata,
                conn=conn
            )
        except Exception as e:
            logger.error(f"Error updating campaign assets: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update campaign assets: {str(e)}"
            )
        
        logger.info(f"Successfully uploaded campaign: {campaign.id}")
        
        return CampaignUploadResponse(
            campaign_id=campaign.id,
            status=campaign.status,
            message="Campaign assets uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading campaign: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload campaign: {str(e)}"
        )

