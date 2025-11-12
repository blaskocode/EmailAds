"""
Performance tracking endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import logging
from datetime import datetime

from app.models.schemas import (
    PerformanceUpdateRequest,
    PerformanceUpdateResponse,
    TestDataGenerationResponse
)
from app.models.campaign import Campaign
from app.database import get_db
from app.services.test_data_generator import generate_test_performance_data

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/campaigns/{campaign_id}/performance", response_model=PerformanceUpdateResponse)
async def update_campaign_performance(
    campaign_id: str,
    request: PerformanceUpdateRequest,
    conn = Depends(get_db)
):
    """
    Update performance metrics for a campaign
    
    This endpoint accepts performance metrics (open rate, click rate, conversion rate)
    from external systems and calculates a performance score.
    """
    try:
        # Get campaign
        campaign = await Campaign.get_by_id(conn, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Update performance metrics
        update_data = {}
        if request.open_rate is not None:
            update_data['open_rate'] = request.open_rate
        if request.click_rate is not None:
            update_data['click_rate'] = request.click_rate
        if request.conversion_rate is not None:
            update_data['conversion_rate'] = request.conversion_rate
        
        # Calculate performance score
        # Weighted average: 40% open rate, 30% click rate, 30% conversion rate
        open_rate = request.open_rate if request.open_rate is not None else campaign.open_rate or 0
        click_rate = request.click_rate if request.click_rate is not None else campaign.click_rate or 0
        conversion_rate = request.conversion_rate if request.conversion_rate is not None else campaign.conversion_rate or 0
        
        performance_score = (
            (open_rate * 0.4) +
            (click_rate * 0.3) +
            (conversion_rate * 0.3)
        )
        
        update_data['performance_score'] = performance_score
        update_data['performance_timestamp'] = datetime.utcnow().isoformat()
        
        # Update campaign
        await campaign.update(conn, **update_data)
        
        logger.info(f"Updated performance metrics for campaign {campaign_id}: score={performance_score:.3f}")
        
        return PerformanceUpdateResponse(
            campaign_id=campaign_id,
            open_rate=update_data.get('open_rate'),
            click_rate=update_data.get('click_rate'),
            conversion_rate=update_data.get('conversion_rate'),
            performance_score=performance_score,
            performance_timestamp=update_data['performance_timestamp'],
            message="Performance metrics updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to update performance metrics")


@router.post("/test/generate-performance-data", response_model=TestDataGenerationResponse)
async def generate_test_data(
    conn = Depends(get_db)
):
    """
    Generate realistic test performance metrics for approved campaigns without performance data
    
    This endpoint is useful for:
    - Demo purposes
    - Testing recommendations functionality
    - Development and QA
    
    Generates varied performance metrics across different tiers:
    - High performers: ~35% of campaigns (open: 25-35%, click: 6-10%, conversion: 3-6%)
    - Medium performers: ~45% of campaigns (open: 15-25%, click: 3-6%, conversion: 1-3%)
    - Low performers: ~20% of campaigns (open: 8-15%, click: 1-3%, conversion: 0.5-1%)
    
    Only updates approved campaigns that don't already have performance data.
    """
    try:
        result = await generate_test_performance_data(conn)
        
        return TestDataGenerationResponse(
            generated=result["generated"],
            message=result["message"],
            summary=result["summary"],
            campaigns=result["campaigns"]
        )
        
    except Exception as e:
        logger.error(f"Error generating test performance data: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate test performance data")

