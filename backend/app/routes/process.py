"""
Process endpoint for AI processing of campaigns
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import time
import logging
import asyncio

from app.models.schemas import ProcessCampaignRequest, ProcessCampaignResponse
from app.services.campaign_service import get_campaign
from app.services.ai_service import process_text_content, process_images_parallel
from app.services.image_service import (
    download_image_from_s3,
    optimize_and_upload_logo,
    optimize_and_upload_hero_images
)
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/process/{campaign_id}", response_model=ProcessCampaignResponse)
async def process_campaign(
    campaign_id: str,
    conn = Depends(get_db)
):
    """
    Process campaign with AI: optimize content and images
    
    This endpoint:
    1. Fetches campaign data
    2. Downloads images from S3
    3. Processes text content with GPT-4
    4. Analyzes images with GPT-4 Vision
    5. Optimizes images
    6. Stores results in database
    
    Target: Complete in <5 seconds
    """
    start_time = time.time()
    
    try:
        # Get campaign
        campaign = await get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        if not campaign.ai_processing_data:
            raise HTTPException(
                status_code=400,
                detail="Campaign assets not found. Please upload assets first."
            )
        
        # The asset metadata structure from upload route:
        # { 'logo': {...}, 'hero_images': [...], 'content': {...} }
        logo_metadata = campaign.ai_processing_data.get('logo', {})
        hero_images_metadata = campaign.ai_processing_data.get('hero_images', [])
        content_data = campaign.ai_processing_data.get('content', {})
        
        # Extract image URLs and content
        logo_s3_url = logo_metadata.get('s3_url') if logo_metadata else None
        hero_s3_urls = [
            hero.get('s3_url')
            for hero in hero_images_metadata
            if hero and hero.get('s3_url')
        ]
        
        subject_line = content_data.get('subject_line')
        body_copy = content_data.get('body_copy')
        cta_text = content_data.get('cta_text')
        
        # Download images from S3 in parallel
        download_tasks = []
        if logo_s3_url:
            download_tasks.append(download_image_from_s3(logo_s3_url))
        for hero_url in hero_s3_urls:
            download_tasks.append(download_image_from_s3(hero_url))
        
        downloaded_images = await asyncio.gather(*download_tasks, return_exceptions=True)
        
        logo_bytes = None
        hero_images_bytes = []
        hero_filenames = []
        
        if logo_s3_url:
            logo_result = downloaded_images[0]
            if isinstance(logo_result, Exception) or logo_result is None:
                logger.warning(f"Failed to download logo: {logo_result}")
            else:
                logo_bytes = logo_result
        
        hero_start_idx = 1 if logo_s3_url else 0
        for idx, hero_url in enumerate(hero_s3_urls):
            hero_result = downloaded_images[hero_start_idx + idx]
            if isinstance(hero_result, Exception) or hero_result is None:
                logger.warning(f"Failed to download hero image {idx}: {hero_result}")
            else:
                hero_images_bytes.append(hero_result)
                hero_meta = hero_images_metadata[idx] if idx < len(hero_images_metadata) else {}
                hero_filenames.append(hero_meta.get('filename', f'hero_{idx}.jpg'))
        
        # Parallel processing: Text + Images + Optimization
        processing_tasks = []
        
        # Text processing
        text_task = process_text_content(subject_line, body_copy, cta_text)
        processing_tasks.append(('text', text_task))
        
        # Image analysis (if images available)
        if logo_bytes or hero_images_bytes:
            image_analysis_task = process_images_parallel(logo_bytes, hero_images_bytes)
            processing_tasks.append(('images', image_analysis_task))
        else:
            image_analysis_task = None
        
        # Run text and image analysis in parallel
        results = await asyncio.gather(
            *[task for _, task in processing_tasks],
            return_exceptions=True
        )
        
        # Extract results
        text_result = None
        image_analysis_result = None
        
        for (task_type, _), result in zip(processing_tasks, results):
            if isinstance(result, Exception):
                logger.error(f"{task_type} processing failed: {result}")
                if task_type == 'text':
                    text_result = {
                        "subject_lines": [subject_line or "Email Campaign"] * 3,
                        "preview_text": content_data.get('preview_text', "Check out our offer!"),
                        "headline": "Special Offer",
                        "body_paragraphs": [body_copy or "Thank you for your interest."],
                        "cta_text": cta_text or "Learn More",
                        "suggestions": "Content processed with fallback"
                    }
            else:
                if task_type == 'text':
                    text_result = result
                elif task_type == 'images':
                    image_analysis_result = result
        
        # Optimize and re-upload images (in parallel)
        optimization_tasks = []
        optimized_logo_url = None
        optimized_hero_urls = []
        
        if logo_bytes:
            logo_filename = logo_metadata.get('filename', 'logo.jpg') if logo_metadata else 'logo.jpg'
            optimization_tasks.append(
                ('logo', optimize_and_upload_logo(logo_bytes, campaign_id, logo_filename))
            )
        
        if hero_images_bytes:
            for idx, hero_bytes in enumerate(hero_images_bytes):
                hero_meta = hero_images_metadata[idx] if idx < len(hero_images_metadata) else {}
                hero_filename = hero_meta.get('filename', f'hero_{idx}.jpg')
                optimization_tasks.append(
                    (f'hero_{idx}', optimize_and_upload_hero_images([hero_bytes], campaign_id, [hero_filename]))
                )
        
        if optimization_tasks:
            opt_results = await asyncio.gather(
                *[task for _, task in optimization_tasks],
                return_exceptions=True
            )
            
            for (task_type, _), result in zip(optimization_tasks, opt_results):
                if isinstance(result, Exception):
                    logger.error(f"{task_type} optimization failed: {result}")
                else:
                    if task_type == 'logo':
                        _, optimized_logo_url = result
                    elif task_type.startswith('hero_'):
                        if result and len(result) > 0:
                            _, hero_url = result[0]
                            optimized_hero_urls.append(hero_url)
        
        # Aggregate AI results
        ai_results = {
            "text_optimization": text_result or {},
            "image_analysis": image_analysis_result or {},
            "optimized_images": {
                "logo": optimized_logo_url,
                "hero_images": optimized_hero_urls
            }
        }
        
        # Update campaign with AI results
        if not hasattr(campaign, 'ai_processing_data'):
            campaign.ai_processing_data = {}
        
        campaign.ai_processing_data['ai_results'] = ai_results
        campaign.status = 'processed'
        
        await campaign.update(conn, ai_processing_data=campaign.ai_processing_data, status='processed')
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(f"Campaign {campaign_id} processed in {processing_time_ms}ms")
        
        return ProcessCampaignResponse(
            campaign_id=campaign_id,
            status='processed',
            preview_url=f"/api/v1/preview/{campaign_id}",
            processing_time_ms=processing_time_ms,
            ai_suggestions=ai_results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing campaign {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process campaign: {str(e)}"
        )

