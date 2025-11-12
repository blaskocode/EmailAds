"""
Campaign review endpoints for editorial review workflow
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
import logging

from app.models.schemas import (
    ReviewCampaignRequest,
    ReviewCampaignResponse,
    CampaignResponse,
    CampaignListResponse
)
from app.services.campaign_service import get_campaign
from app.models.campaign import Campaign
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/campaigns/{campaign_id}/review", response_model=ReviewCampaignResponse)
async def review_campaign(
    campaign_id: str,
    request: ReviewCampaignRequest,
    conn = Depends(get_db)
):
    """
    Review a campaign (editorial review step)
    
    Args:
    - campaign_id: Campaign ID to review
    - review_status: Status of the review (pending, reviewed, approved, rejected)
    - reviewer_notes: Optional notes from the reviewer
    
    Returns:
    - Review response with updated review status
    """
    try:
        campaign = await get_campaign(campaign_id, conn=conn)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Update campaign with review information
        await campaign.update(
            conn,
            review_status=request.review_status,
            reviewer_notes=request.reviewer_notes
        )
        
        logger.info(
            f"Campaign {campaign_id} reviewed with status '{request.review_status}'"
        )
        
        return ReviewCampaignResponse(
            campaign_id=campaign_id,
            review_status=request.review_status,
            reviewer_notes=request.reviewer_notes,
            message=f"Campaign review status updated to '{request.review_status}'"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reviewing campaign {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to review campaign: {str(e)}"
        )


@router.get("/campaigns/review/list", response_model=CampaignListResponse)
async def list_campaigns_by_review_status(
    review_status: Optional[str] = Query(None, description="Filter by review status (pending, reviewed, approved, rejected)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of campaigns to return"),
    offset: int = Query(0, ge=0, description="Number of campaigns to skip"),
    conn = Depends(get_db)
):
    """
    List campaigns filtered by review status
    
    Returns:
    - List of campaigns with specified review status
    """
    try:
        if review_status:
            campaigns = await Campaign.get_by_review_status(conn, review_status, limit=limit, offset=offset)
            # Count total matching campaigns
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT COUNT(*) as total FROM campaigns WHERE review_status = ?
                """, (review_status,))
                result = await cursor.fetchone()
                total = result['total'] if result else 0
        else:
            # Get all campaigns with any review status (not null)
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT * FROM campaigns 
                    WHERE review_status IS NOT NULL
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                rows = await cursor.fetchall()
                campaigns = [Campaign.from_row(dict(row)) for row in rows]
                
                await cursor.execute("SELECT COUNT(*) as total FROM campaigns WHERE review_status IS NOT NULL")
                result = await cursor.fetchone()
                total = result['total'] if result else 0
        
        # Convert to response format
        campaign_responses = [
            CampaignResponse(
                id=c.id,
                campaign_name=c.campaign_name,
                advertiser_name=c.advertiser_name,
                status=c.status,
                created_at=c.created_at,
                approved_at=c.approved_at,
                assets_s3_path=c.assets_s3_path,
                html_s3_path=c.html_s3_path,
                proof_s3_path=c.proof_s3_path,
                feedback=c.feedback,
                ai_processing_data=c.ai_processing_data,
                scheduled_at=c.scheduled_at,
                scheduling_status=c.scheduling_status,
                review_status=c.review_status,
                reviewer_notes=c.reviewer_notes
            )
            for c in campaigns
        ]
        
        return CampaignListResponse(
            campaigns=campaign_responses,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error listing campaigns by review status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list campaigns: {str(e)}"
        )

