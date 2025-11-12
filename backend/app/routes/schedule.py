"""
Campaign scheduling endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import logging

from app.models.schemas import (
    ScheduleCampaignRequest,
    ScheduleCampaignResponse,
    CancelScheduleResponse,
    CampaignResponse
)
from app.services.campaign_service import get_campaign
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/campaigns/{campaign_id}/schedule", response_model=ScheduleCampaignResponse)
async def schedule_campaign(
    campaign_id: str,
    request: ScheduleCampaignRequest,
    conn = Depends(get_db)
):
    """
    Schedule a campaign for future sending
    
    Args:
    - campaign_id: Campaign ID to schedule
    - scheduled_at: ISO 8601 datetime string (must be in the future)
    
    Returns:
    - Campaign scheduling details
    """
    try:
        campaign = await get_campaign(campaign_id, conn=conn)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Only allow scheduling approved campaigns
        if campaign.status != 'approved':
            raise HTTPException(
                status_code=400,
                detail=f"Cannot schedule campaign with status '{campaign.status}'. Only approved campaigns can be scheduled."
            )
        
        # Parse and validate scheduled_at datetime
        try:
            scheduled_datetime = datetime.fromisoformat(request.scheduled_at.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid datetime format. Use ISO 8601 format (e.g., '2025-12-01T10:00:00Z')"
            )
        
        # Validate that scheduled time is in the future
        now = datetime.utcnow()
        if scheduled_datetime.replace(tzinfo=None) <= now:
            raise HTTPException(
                status_code=400,
                detail="Scheduled time must be in the future"
            )
        
        # Update campaign with scheduling information
        await campaign.update(
            conn,
            scheduled_at=request.scheduled_at,
            scheduling_status='scheduled'
        )
        
        logger.info(f"Scheduled campaign {campaign_id} for {request.scheduled_at}")
        
        return ScheduleCampaignResponse(
            campaign_id=campaign_id,
            scheduled_at=request.scheduled_at,
            scheduling_status='scheduled',
            message=f"Campaign scheduled for {request.scheduled_at}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling campaign {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to schedule campaign: {str(e)}"
        )


@router.post("/campaigns/{campaign_id}/cancel-schedule", response_model=CancelScheduleResponse)
async def cancel_schedule(
    campaign_id: str,
    conn = Depends(get_db)
):
    """
    Cancel a scheduled campaign
    
    Args:
    - campaign_id: Campaign ID to cancel scheduling for
    
    Returns:
    - Cancellation confirmation
    """
    try:
        campaign = await get_campaign(campaign_id, conn=conn)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Only allow canceling scheduled campaigns
        if campaign.scheduling_status != 'scheduled':
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel schedule for campaign with scheduling_status '{campaign.scheduling_status}'. Only scheduled campaigns can be canceled."
            )
        
        # Clear scheduling information
        await campaign.update(
            conn,
            scheduled_at=None,
            scheduling_status=None
        )
        
        logger.info(f"Canceled schedule for campaign {campaign_id}")
        
        return CancelScheduleResponse(
            campaign_id=campaign_id,
            message="Campaign schedule canceled successfully",
            scheduling_status=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error canceling schedule for campaign {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel schedule: {str(e)}"
        )

