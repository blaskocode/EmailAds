"""
Preview endpoint for retrieving campaign preview data
"""
from fastapi import APIRouter, HTTPException, Depends
import logging

from app.models.schemas import PreviewResponse
from app.services.campaign_service import get_campaign
from app.services.proof_service import generate_proof
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/preview/{campaign_id}", response_model=PreviewResponse)
async def get_campaign_preview(
    campaign_id: str,
    conn = Depends(get_db)
):
    """
    Get preview data for a campaign
    
    This endpoint:
    1. Fetches campaign data
    2. Generates proof if not already generated (or uses cached)
    3. Returns preview data including HTML and metadata
    
    If campaign status is 'ready', uses cached proof.
    If campaign status is 'processed', generates proof first.
    """
    try:
        # Get campaign
        campaign = await get_campaign(campaign_id, conn=conn)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # If campaign is ready, use cached proof (fast path)
        # If processed but not ready, generate proof
        # If uploaded but not processed, need to process first
        if campaign.status == 'ready' and campaign.proof_s3_path:
            # Campaign already has proof, generate preview data from it
            proof_result = await generate_proof(campaign_id, campaign, use_cache=True)
        elif campaign.status == 'processed':
            # Generate proof for processed campaign
            proof_result = await generate_proof(campaign_id, campaign, use_cache=False)
        elif campaign.status == 'uploaded':
            # Campaign needs to be processed first
            raise HTTPException(
                status_code=400,
                detail="Campaign must be processed before preview. Please process the campaign first."
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Campaign is in invalid state for preview. Current status: {campaign.status}"
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preview for campaign {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get preview: {str(e)}"
        )

