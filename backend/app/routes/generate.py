"""
Generate endpoint for proof generation
"""
from fastapi import APIRouter, HTTPException, Depends
import logging
import time

from app.models.schemas import PreviewResponse
from app.services.proof_service import generate_proof, update_campaign_with_proof
from app.services.campaign_service import get_campaign
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate/{campaign_id}", response_model=PreviewResponse)
async def generate_campaign_proof(
    campaign_id: str,
    conn = Depends(get_db)
):
    """
    Generate email proof for a processed campaign
    
    This endpoint:
    1. Fetches campaign data and AI processing results
    2. Generates HTML email using template service
    3. Uploads proof to S3
    4. Updates campaign status to 'ready'
    5. Returns preview data
    
    Target: Complete in <2 seconds
    """
    start_time = time.time()
    
    try:
        # Get campaign
        campaign = await get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Generate proof
        proof_result = await generate_proof(campaign_id, campaign)
        
        # Update campaign with proof URL and set status to 'ready'
        await update_campaign_with_proof(
            campaign_id,
            proof_result['proof_s3_url'],
            conn
        )
        
        total_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            f"Proof generation completed for campaign {campaign_id} in {total_time_ms}ms"
        )
        
        # Return preview response
        preview_data = proof_result['preview_data']
        return PreviewResponse(
            campaign_id=campaign_id,
            html_preview=preview_data['html_preview'],
            assets=preview_data['assets'],
            ai_suggestions=preview_data['ai_suggestions'],
            metadata=preview_data['metadata']
        )
        
    except ValueError as e:
        logger.warning(f"Validation error generating proof: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating proof for campaign {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate proof: {str(e)}"
        )


@router.post("/campaigns/{campaign_id}/regenerate", response_model=PreviewResponse)
async def regenerate_campaign_proof(
    campaign_id: str,
    conn = Depends(get_db)
):
    """
    Regenerate email proof for a campaign with updated content/images
    
    This endpoint:
    1. Fetches latest campaign data (including any edits)
    2. Regenerates HTML email using template service
    3. Uploads new proof to S3
    4. Updates campaign status to 'ready'
    5. Returns preview data
    
    Target: Complete in <2 seconds
    """
    start_time = time.time()
    
    try:
        # Get campaign
        campaign = await get_campaign(campaign_id, conn=conn)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Clear proof cache to force regeneration
        from app.services.proof_service import _proof_cache
        if campaign_id in _proof_cache:
            del _proof_cache[campaign_id]
        
        # Generate proof (will use latest campaign data)
        proof_result = await generate_proof(campaign_id, campaign, use_cache=False)
        
        # Update campaign with proof URL and set status to 'ready'
        await update_campaign_with_proof(
            campaign_id,
            proof_result['proof_s3_url'],
            conn
        )
        
        total_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            f"Proof regenerated for campaign {campaign_id} in {total_time_ms}ms"
        )
        
        # Return preview response
        preview_data = proof_result['preview_data']
        return PreviewResponse(
            campaign_id=campaign_id,
            html_preview=preview_data['html_preview'],
            assets=preview_data['assets'],
            ai_suggestions=preview_data['ai_suggestions'],
            metadata=preview_data['metadata']
        )
        
    except ValueError as e:
        logger.warning(f"Validation error regenerating proof: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating proof for campaign {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate proof: {str(e)}"
        )

