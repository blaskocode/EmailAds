"""
Recommendation service for generating AI-based content suggestions
"""
from typing import Dict, List, Optional, Any
import logging
from app.models.campaign import Campaign
from app.services.analytics_service import aggregate_campaign_performance

logger = logging.getLogger(__name__)


async def generate_recommendations(
    conn,
    campaign: Campaign,
    analytics_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate personalized recommendations for a campaign based on historical performance
    
    Args:
        conn: Database connection
        campaign: Campaign to generate recommendations for
        analytics_data: Pre-computed analytics (optional, will fetch if not provided)
        
    Returns:
        Dictionary with recommendations
    """
    try:
        # Get analytics if not provided
        if analytics_data is None:
            analytics_data = await aggregate_campaign_performance(conn)
        
        has_data = analytics_data.get("has_sufficient_data", False)
        total_campaigns = analytics_data.get("total_campaigns", 0)
        
        if not has_data:
            logger.info("Insufficient historical data for recommendations")
            return {
                "subject_line_recommendations": [],
                "preview_text_recommendations": [],
                "cta_text_recommendations": [],
                "content_structure_suggestions": None,
                "image_optimization_suggestions": None,
                "historical_data_available": False,
                "total_campaigns_analyzed": total_campaigns
            }
        
        analytics = analytics_data.get("analytics", {})
        
        # Generate recommendations based on patterns
        recommendations = {
            "subject_line_recommendations": _recommend_subject_lines(
                campaign, analytics.get("subject_line_patterns", {})
            ),
            "preview_text_recommendations": _recommend_preview_texts(
                campaign, analytics.get("preview_text_patterns", {})
            ),
            "cta_text_recommendations": _recommend_cta_texts(
                campaign, analytics.get("cta_patterns", {})
            ),
            "content_structure_suggestions": _suggest_content_structure(
                campaign, analytics
            ),
            "image_optimization_suggestions": _suggest_image_optimization(
                campaign, analytics.get("image_patterns", {})
            ),
            "historical_data_available": True,
            "total_campaigns_analyzed": total_campaigns
        }
        
        logger.info(f"Generated recommendations for campaign {campaign.id}")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return {
            "subject_line_recommendations": [],
            "preview_text_recommendations": [],
            "cta_text_recommendations": [],
            "content_structure_suggestions": None,
            "image_optimization_suggestions": None,
            "historical_data_available": False,
            "total_campaigns_analyzed": 0
        }


def _recommend_subject_lines(
    campaign: Campaign,
    patterns: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Generate subject line recommendations"""
    recommendations = []
    
    if not patterns or not patterns.get("top_subject_lines"):
        return recommendations
    
    top_subjects = patterns["top_subject_lines"][:5]  # Top 5
    avg_performance = patterns.get("average_performance_score", 0)
    
    for idx, subject_data in enumerate(top_subjects):
        confidence = min(0.95, 0.7 + (avg_performance * 0.25))
        recommendations.append({
            "content": subject_data["text"],
            "confidence_score": confidence,
            "reasoning": f"Based on {patterns.get('sample_count', 0)} high-performing campaigns with average open rate of {patterns.get('average_open_rate', 0):.1%}",
            "based_on_count": patterns.get("sample_count", 0)
        })
    
    return recommendations


def _recommend_preview_texts(
    campaign: Campaign,
    patterns: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Generate preview text recommendations"""
    recommendations = []
    
    if not patterns or not patterns.get("top_preview_texts"):
        return recommendations
    
    top_previews = patterns["top_preview_texts"][:5]
    avg_performance = patterns.get("average_performance_score", 0)
    
    for preview_data in top_previews:
        confidence = min(0.95, 0.7 + (avg_performance * 0.25))
        recommendations.append({
            "content": preview_data["text"],
            "confidence_score": confidence,
            "reasoning": f"Based on {patterns.get('sample_count', 0)} high-performing campaigns with average open rate of {patterns.get('average_open_rate', 0):.1%}",
            "based_on_count": patterns.get("sample_count", 0)
        })
    
    return recommendations


def _recommend_cta_texts(
    campaign: Campaign,
    patterns: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Generate CTA text recommendations"""
    recommendations = []
    
    if not patterns or not patterns.get("top_cta_texts"):
        return recommendations
    
    top_ctas = patterns["top_cta_texts"][:5]
    avg_performance = patterns.get("average_performance_score", 0)
    
    for cta_data in top_ctas:
        confidence = min(0.95, 0.7 + (avg_performance * 0.25))
        recommendations.append({
            "content": cta_data["text"],
            "confidence_score": confidence,
            "reasoning": f"Based on {patterns.get('sample_count', 0)} high-performing campaigns with average click rate of {patterns.get('average_click_rate', 0):.1%}",
            "based_on_count": patterns.get("sample_count", 0)
        })
    
    return recommendations


def _suggest_content_structure(
    campaign: Campaign,
    analytics: Dict[str, Any]
) -> Optional[str]:
    """Generate content structure suggestions"""
    if not analytics:
        return None
    
    overall = analytics.get("overall_averages", {})
    if not overall:
        return None
    
    suggestions = []
    
    # Analyze current campaign structure
    if campaign.ai_processing_data and campaign.ai_processing_data.get('content'):
        content = campaign.ai_processing_data['content']
        if isinstance(content, dict):
            # Check body length
            body = content.get('body_copy', '')
            if len(body) < 100:
                suggestions.append("Consider expanding body copy to 100-150 words for better engagement")
            elif len(body) > 300:
                suggestions.append("Consider shortening body copy to 150-200 words for better readability")
    
    # Add general suggestions based on averages
    avg_open = overall.get("average_open_rate", 0)
    avg_click = overall.get("average_click_rate", 0)
    
    if avg_open > 0.25:
        suggestions.append("High-performing campaigns typically use clear, benefit-focused headlines")
    
    if avg_click > 0.05:
        suggestions.append("Strong CTAs placed prominently tend to improve click rates")
    
    return "; ".join(suggestions) if suggestions else None


def _suggest_image_optimization(
    campaign: Campaign,
    patterns: Dict[str, Any]
) -> Optional[str]:
    """Generate image optimization suggestions"""
    if not patterns:
        return None
    
    # Get current campaign image count
    current_hero_count = 0
    has_logo = False
    
    if campaign.ai_processing_data and campaign.ai_processing_data.get('optimized_images'):
        images = campaign.ai_processing_data['optimized_images']
        if isinstance(images, dict):
            current_hero_count = len(images.get('hero_images', []))
            has_logo = bool(images.get('logo'))
    
    avg_hero_count = patterns.get("average_hero_count", 0)
    
    suggestions = []
    
    if not has_logo:
        suggestions.append("Consider adding a logo for brand recognition")
    
    if current_hero_count < avg_hero_count:
        suggestions.append(f"High-performing campaigns typically use {avg_hero_count:.1f} hero images on average")
    elif current_hero_count > avg_hero_count + 1:
        suggestions.append(f"Consider reducing hero images to {int(avg_hero_count)} for optimal performance")
    
    return "; ".join(suggestions) if suggestions else None

