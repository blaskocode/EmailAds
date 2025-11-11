"""
Campaign status endpoint
"""
from fastapi import APIRouter, HTTPException, Depends
import logging

from app.models.schemas import CampaignStatusResponse
from app.services.campaign_service import get_campaign
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/campaigns/{campaign_id}/status", response_model=CampaignStatusResponse)
async def get_campaign_status(
    campaign_id: str,
    conn = Depends(get_db)
):
    """
    Get campaign status
    
    Returns:
    - campaign_id: Campaign ID
    - status: Current campaign status (draft, uploaded, processed, ready, approved, rejected)
    - can_preview: Whether preview is available (status is 'ready' or 'processed')
    """
    try:
        campaign = await get_campaign(campaign_id, conn=conn)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        can_preview = campaign.status in ['ready', 'processed']
        
        return CampaignStatusResponse(
            campaign_id=campaign_id,
            status=campaign.status,
            can_preview=can_preview
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign status for {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get campaign status: {str(e)}"
        )

