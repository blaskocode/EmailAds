"""
Campaign management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
import logging

from app.models.schemas import (
    CampaignStatusResponse,
    CampaignResponse,
    CampaignListResponse
)
from app.services.campaign_service import get_campaign
from app.models.campaign import Campaign
from app.database import get_db
from app.services.s3_service import s3_service
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/campaigns", response_model=CampaignListResponse)
async def list_campaigns(
    status: Optional[str] = Query(None, description="Filter by status (draft, uploaded, processed, ready, approved, rejected)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of campaigns to return"),
    offset: int = Query(0, ge=0, description="Number of campaigns to skip"),
    conn = Depends(get_db)
):
    """
    List all campaigns with optional status filtering and pagination
    
    Returns:
    - campaigns: List of campaign objects
    - total: Total number of campaigns (before pagination)
    - limit: Number of campaigns per page
    - offset: Number of campaigns skipped
    """
    try:
        # Get campaigns based on status filter
        if status:
            campaigns = await Campaign.get_by_status(conn, status, limit=limit, offset=offset)
            # For status filtering, we need to count total matching campaigns
            async with conn.cursor() as cursor:
                await cursor.execute("""
                    SELECT COUNT(*) as total FROM campaigns WHERE status = ?
                """, (status,))
                result = await cursor.fetchone()
                total = result['total'] if result else 0
        else:
            campaigns = await Campaign.get_all(conn, limit=limit, offset=offset)
            # Count total campaigns
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT COUNT(*) as total FROM campaigns")
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
                ai_processing_data=c.ai_processing_data
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
        logger.error(f"Error listing campaigns: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list campaigns: {str(e)}"
        )


def extract_s3_key(s3_url: str) -> Optional[str]:
    """Extract S3 key from s3://bucket/key format"""
    if not s3_url or not s3_url.startswith('s3://'):
        return None
    parts = s3_url.replace('s3://', '').split('/', 1)
    return parts[1] if len(parts) == 2 else None


async def convert_s3_urls_to_presigned(ai_processing_data: Optional[dict]) -> Optional[dict]:
    """
    Convert S3 URLs in ai_processing_data to presigned URLs for frontend access
    """
    if not ai_processing_data:
        return None
    
    import copy
    result = copy.deepcopy(ai_processing_data)
    
    # Convert logo S3 URL to presigned URL
    if result.get('logo') and result['logo'].get('s3_url'):
        logo_s3_url = result['logo']['s3_url']
        logo_key = extract_s3_key(logo_s3_url)
        if logo_key:
            try:
                presigned_url = await s3_service.get_presigned_url(logo_key, expiration=3600)
                result['logo']['presigned_url'] = presigned_url
            except Exception as e:
                logger.warning(f"Failed to generate presigned URL for logo: {e}")
    
    # Convert hero images S3 URLs to presigned URLs
    if result.get('hero_images'):
        for hero_img in result['hero_images']:
            if hero_img and hero_img.get('s3_url'):
                hero_s3_url = hero_img['s3_url']
                hero_key = extract_s3_key(hero_s3_url)
                if hero_key:
                    try:
                        presigned_url = await s3_service.get_presigned_url(hero_key, expiration=3600)
                        hero_img['presigned_url'] = presigned_url
                    except Exception as e:
                        logger.warning(f"Failed to generate presigned URL for hero image: {e}")
    
    return result


@router.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign_detail(
    campaign_id: str,
    conn = Depends(get_db)
):
    """
    Get full campaign details by ID
    
    Returns:
    - Full campaign object including all fields and feedback
    - ai_processing_data includes presigned URLs for files
    """
    try:
        campaign = await get_campaign(campaign_id, conn=conn)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Convert S3 URLs to presigned URLs in ai_processing_data
        ai_data_with_presigned = await convert_s3_urls_to_presigned(campaign.ai_processing_data)
        
        return CampaignResponse(
            id=campaign.id,
            campaign_name=campaign.campaign_name,
            advertiser_name=campaign.advertiser_name,
            status=campaign.status,
            created_at=campaign.created_at,
            approved_at=campaign.approved_at,
            assets_s3_path=campaign.assets_s3_path,
            html_s3_path=campaign.html_s3_path,
            proof_s3_path=campaign.proof_s3_path,
            feedback=campaign.feedback,
            ai_processing_data=ai_data_with_presigned
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign detail for {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get campaign detail: {str(e)}"
        )


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


@router.post("/campaigns/{campaign_id}/reset", response_model=CampaignResponse)
async def reset_campaign(
    campaign_id: str,
    clear_feedback: bool = Query(False, description="Whether to clear feedback when resetting"),
    conn = Depends(get_db)
):
    """
    Reset a rejected campaign to 'uploaded' status to allow resubmission
    
    Args:
    - campaign_id: Campaign ID to reset
    - clear_feedback: If true, clears the feedback field
    
    Returns:
    - Updated campaign object
    """
    try:
        campaign = await get_campaign(campaign_id, conn=conn)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Only allow resetting rejected campaigns
        if campaign.status != 'rejected':
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reset campaign with status '{campaign.status}'. Only rejected campaigns can be reset."
            )
        
        # Reset to uploaded status
        update_data = {'status': 'uploaded'}
        if clear_feedback:
            update_data['feedback'] = None
        
        await campaign.update(conn, **update_data)
        
        logger.info(f"Reset campaign {campaign_id} to uploaded status")
        
        return CampaignResponse(
            id=campaign.id,
            campaign_name=campaign.campaign_name,
            advertiser_name=campaign.advertiser_name,
            status=campaign.status,
            created_at=campaign.created_at,
            approved_at=campaign.approved_at,
            assets_s3_path=campaign.assets_s3_path,
            html_s3_path=campaign.html_s3_path,
            proof_s3_path=campaign.proof_s3_path,
            feedback=campaign.feedback,
            ai_processing_data=campaign.ai_processing_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting campaign {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset campaign: {str(e)}"
        )

