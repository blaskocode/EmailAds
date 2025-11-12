"""
Analytics service for aggregating campaign performance data
"""
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
from app.models.campaign import Campaign

logger = logging.getLogger(__name__)


async def aggregate_campaign_performance(conn, min_campaigns: int = 5) -> Dict[str, Any]:
    """
    Aggregate campaign performance data to identify patterns
    
    Args:
        conn: Database connection
        min_campaigns: Minimum number of campaigns needed for meaningful analytics
        
    Returns:
        Dictionary with aggregated analytics
    """
    try:
        # Get all approved campaigns with performance data
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM campaigns 
                WHERE status = 'approved' 
                AND performance_score IS NOT NULL
                AND performance_score > 0
                ORDER BY performance_score DESC
            """)
            rows = await cursor.fetchall()
        
        campaigns = [Campaign.from_row(dict(row)) for row in rows]
        
        if len(campaigns) < min_campaigns:
            logger.info(f"Insufficient data for analytics: {len(campaigns)} campaigns (need {min_campaigns})")
            return {
                "has_sufficient_data": False,
                "total_campaigns": len(campaigns),
                "analytics": {}
            }
        
        # Calculate averages by pattern
        analytics = {
            "subject_line_patterns": _analyze_subject_lines(campaigns),
            "preview_text_patterns": _analyze_preview_texts(campaigns),
            "cta_patterns": _analyze_cta_texts(campaigns),
            "image_patterns": _analyze_image_patterns(campaigns),
            "overall_averages": _calculate_overall_averages(campaigns)
        }
        
        logger.info(f"Aggregated analytics from {len(campaigns)} campaigns")
        return {
            "has_sufficient_data": True,
            "total_campaigns": len(campaigns),
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Error aggregating campaign performance: {e}")
        return {
            "has_sufficient_data": False,
            "total_campaigns": 0,
            "analytics": {}
        }


def _analyze_subject_lines(campaigns: List[Campaign]) -> Dict[str, Any]:
    """Analyze subject line patterns from high-performing campaigns"""
    if not campaigns:
        return {}
    
    # Get top 20% performers
    top_performers = campaigns[:max(1, len(campaigns) // 5)]
    
    subject_lines = []
    for campaign in top_performers:
        if campaign.ai_processing_data and campaign.ai_processing_data.get('content'):
            content = campaign.ai_processing_data['content']
            if isinstance(content, dict):
                subject = content.get('subject_line') or content.get('subject_lines', [None])[0]
                if subject:
                    subject_lines.append({
                        "text": subject,
                        "performance_score": campaign.performance_score or 0,
                        "open_rate": campaign.open_rate or 0
                    })
    
    if not subject_lines:
        return {}
    
    # Calculate average performance
    avg_performance = sum(s["performance_score"] for s in subject_lines) / len(subject_lines)
    avg_open_rate = sum(s["open_rate"] for s in subject_lines) / len(subject_lines)
    
    return {
        "top_subject_lines": subject_lines[:10],  # Top 10
        "average_performance_score": avg_performance,
        "average_open_rate": avg_open_rate,
        "sample_count": len(subject_lines)
    }


def _analyze_preview_texts(campaigns: List[Campaign]) -> Dict[str, Any]:
    """Analyze preview text patterns from high-performing campaigns"""
    if not campaigns:
        return {}
    
    top_performers = campaigns[:max(1, len(campaigns) // 5)]
    
    preview_texts = []
    for campaign in top_performers:
        if campaign.ai_processing_data and campaign.ai_processing_data.get('content'):
            content = campaign.ai_processing_data['content']
            if isinstance(content, dict):
                preview = content.get('preview_text')
                if preview:
                    preview_texts.append({
                        "text": preview,
                        "performance_score": campaign.performance_score or 0,
                        "open_rate": campaign.open_rate or 0
                    })
    
    if not preview_texts:
        return {}
    
    avg_performance = sum(p["performance_score"] for p in preview_texts) / len(preview_texts)
    avg_open_rate = sum(p["open_rate"] for p in preview_texts) / len(preview_texts)
    
    return {
        "top_preview_texts": preview_texts[:10],
        "average_performance_score": avg_performance,
        "average_open_rate": avg_open_rate,
        "sample_count": len(preview_texts)
    }


def _analyze_cta_texts(campaigns: List[Campaign]) -> Dict[str, Any]:
    """Analyze CTA text patterns from high-performing campaigns"""
    if not campaigns:
        return {}
    
    top_performers = campaigns[:max(1, len(campaigns) // 5)]
    
    cta_texts = []
    for campaign in top_performers:
        if campaign.ai_processing_data and campaign.ai_processing_data.get('content'):
            content = campaign.ai_processing_data['content']
            if isinstance(content, dict):
                cta = content.get('cta_text')
                if cta:
                    cta_texts.append({
                        "text": cta,
                        "performance_score": campaign.performance_score or 0,
                        "click_rate": campaign.click_rate or 0,
                        "conversion_rate": campaign.conversion_rate or 0
                    })
    
    if not cta_texts:
        return {}
    
    avg_performance = sum(c["performance_score"] for c in cta_texts) / len(cta_texts)
    avg_click_rate = sum(c["click_rate"] for c in cta_texts) / len(cta_texts)
    avg_conversion_rate = sum(c["conversion_rate"] for c in cta_texts) / len(cta_texts)
    
    return {
        "top_cta_texts": cta_texts[:10],
        "average_performance_score": avg_performance,
        "average_click_rate": avg_click_rate,
        "average_conversion_rate": avg_conversion_rate,
        "sample_count": len(cta_texts)
    }


def _analyze_image_patterns(campaigns: List[Campaign]) -> Dict[str, Any]:
    """Analyze image count and type patterns from high-performing campaigns"""
    if not campaigns:
        return {}
    
    top_performers = campaigns[:max(1, len(campaigns) // 5)]
    
    image_counts = []
    for campaign in top_performers:
        if campaign.ai_processing_data and campaign.ai_processing_data.get('optimized_images'):
            images = campaign.ai_processing_data['optimized_images']
            if isinstance(images, dict):
                hero_count = len(images.get('hero_images', []))
                has_logo = bool(images.get('logo'))
                image_counts.append({
                    "hero_count": hero_count,
                    "has_logo": has_logo,
                    "total_images": hero_count + (1 if has_logo else 0),
                    "performance_score": campaign.performance_score or 0
                })
    
    if not image_counts:
        return {}
    
    avg_hero_count = sum(i["hero_count"] for i in image_counts) / len(image_counts)
    avg_total_images = sum(i["total_images"] for i in image_counts) / len(image_counts)
    avg_performance = sum(i["performance_score"] for i in image_counts) / len(image_counts)
    
    return {
        "average_hero_count": avg_hero_count,
        "average_total_images": avg_total_images,
        "average_performance_score": avg_performance,
        "sample_count": len(image_counts)
    }


def _calculate_overall_averages(campaigns: List[Campaign]) -> Dict[str, float]:
    """Calculate overall average performance metrics"""
    if not campaigns:
        return {}
    
    total = len(campaigns)
    return {
        "average_open_rate": sum(c.open_rate or 0 for c in campaigns) / total,
        "average_click_rate": sum(c.click_rate or 0 for c in campaigns) / total,
        "average_conversion_rate": sum(c.conversion_rate or 0 for c in campaigns) / total,
        "average_performance_score": sum(c.performance_score or 0 for c in campaigns) / total
    }

