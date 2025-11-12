"""
Recommendations endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
import logging

from app.models.schemas import (
    RecommendationsResponse,
    RecommendationItem
)
from app.models.campaign import Campaign
from app.database import get_db
from app.services.recommendation_service import generate_recommendations

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/campaigns/{campaign_id}/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    campaign_id: str,
    conn = Depends(get_db)
):
    """
    Get AI-based content recommendations for a campaign based on past performance
    
    Returns personalized suggestions for:
    - Subject lines (top 3-5)
    - Preview texts (top 3-5)
    - CTA texts (top 3-5)
    - Content structure suggestions
    - Image optimization suggestions
    """
    try:
        # Get campaign
        campaign = await Campaign.get_by_id(conn, campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Generate recommendations
        recommendations = await generate_recommendations(conn, campaign)
        
        # Convert to response format
        return RecommendationsResponse(
            campaign_id=campaign_id,
            subject_line_recommendations=[
                RecommendationItem(**rec) for rec in recommendations.get("subject_line_recommendations", [])
            ],
            preview_text_recommendations=[
                RecommendationItem(**rec) for rec in recommendations.get("preview_text_recommendations", [])
            ],
            cta_text_recommendations=[
                RecommendationItem(**rec) for rec in recommendations.get("cta_text_recommendations", [])
            ],
            content_structure_suggestions=recommendations.get("content_structure_suggestions"),
            image_optimization_suggestions=recommendations.get("image_optimization_suggestions"),
            historical_data_available=recommendations.get("historical_data_available", False),
            total_campaigns_analyzed=recommendations.get("total_campaigns_analyzed", 0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")

