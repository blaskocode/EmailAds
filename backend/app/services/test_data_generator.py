"""
Test data generator service for creating realistic performance metrics for demo purposes
"""
import random
import logging
from typing import Dict, List, Any
from datetime import datetime
from app.models.campaign import Campaign

logger = logging.getLogger(__name__)


async def generate_test_performance_data(conn) -> Dict[str, Any]:
    """
    Generate realistic test performance metrics for approved campaigns without performance data
    
    Creates varied performance metrics across different tiers:
    - High performers: 30-40% of campaigns
    - Medium performers: 40-50% of campaigns  
    - Low performers: 20-30% of campaigns
    
    Args:
        conn: Database connection
        
    Returns:
        Dictionary with summary of generated data
    """
    try:
        # Get all approved campaigns without performance data
        async with conn.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM campaigns 
                WHERE status = 'approved' 
                AND (performance_score IS NULL OR performance_score = 0)
                ORDER BY created_at DESC
            """)
            rows = await cursor.fetchall()
        
        campaigns = [Campaign.from_row(dict(row)) for row in rows]
        
        if not campaigns:
            logger.info("No approved campaigns without performance data found")
            return {
                "generated": 0,
                "campaigns": [],
                "message": "No approved campaigns found without performance data"
            }
        
        # Distribute campaigns across performance tiers
        total = len(campaigns)
        high_count = max(1, int(total * 0.35))  # ~35% high performers
        medium_count = max(1, int(total * 0.45))  # ~45% medium performers
        low_count = total - high_count - medium_count  # Remaining low performers
        
        # Shuffle to randomize distribution
        random.shuffle(campaigns)
        
        generated_campaigns = []
        
        # Generate high performer metrics
        for i in range(high_count):
            campaign = campaigns[i]
            metrics = _generate_high_performer_metrics()
            await _update_campaign_performance(conn, campaign, metrics)
            generated_campaigns.append({
                "campaign_id": campaign.id,
                "campaign_name": campaign.campaign_name,
                "tier": "high",
                **metrics
            })
        
        # Generate medium performer metrics
        for i in range(high_count, high_count + medium_count):
            campaign = campaigns[i]
            metrics = _generate_medium_performer_metrics()
            await _update_campaign_performance(conn, campaign, metrics)
            generated_campaigns.append({
                "campaign_id": campaign.id,
                "campaign_name": campaign.campaign_name,
                "tier": "medium",
                **metrics
            })
        
        # Generate low performer metrics
        for i in range(high_count + medium_count, total):
            campaign = campaigns[i]
            metrics = _generate_low_performer_metrics()
            await _update_campaign_performance(conn, campaign, metrics)
            generated_campaigns.append({
                "campaign_id": campaign.id,
                "campaign_name": campaign.campaign_name,
                "tier": "low",
                **metrics
            })
        
        logger.info(f"Generated test performance data for {total} campaigns")
        
        return {
            "generated": total,
            "campaigns": generated_campaigns,
            "summary": {
                "high_performers": high_count,
                "medium_performers": medium_count,
                "low_performers": low_count
            },
            "message": f"Successfully generated test performance data for {total} campaigns"
        }
        
    except Exception as e:
        logger.error(f"Error generating test performance data: {e}")
        raise


def _generate_high_performer_metrics() -> Dict[str, float]:
    """Generate metrics for high-performing campaigns"""
    open_rate = round(random.uniform(0.25, 0.35), 3)
    click_rate = round(random.uniform(0.06, 0.10), 3)
    conversion_rate = round(random.uniform(0.03, 0.06), 3)
    
    performance_score = round(
        (open_rate * 0.4) + (click_rate * 0.3) + (conversion_rate * 0.3),
        3
    )
    
    return {
        "open_rate": open_rate,
        "click_rate": click_rate,
        "conversion_rate": conversion_rate,
        "performance_score": performance_score
    }


def _generate_medium_performer_metrics() -> Dict[str, float]:
    """Generate metrics for medium-performing campaigns"""
    open_rate = round(random.uniform(0.15, 0.25), 3)
    click_rate = round(random.uniform(0.03, 0.06), 3)
    conversion_rate = round(random.uniform(0.01, 0.03), 3)
    
    performance_score = round(
        (open_rate * 0.4) + (click_rate * 0.3) + (conversion_rate * 0.3),
        3
    )
    
    return {
        "open_rate": open_rate,
        "click_rate": click_rate,
        "conversion_rate": conversion_rate,
        "performance_score": performance_score
    }


def _generate_low_performer_metrics() -> Dict[str, float]:
    """Generate metrics for low-performing campaigns"""
    open_rate = round(random.uniform(0.08, 0.15), 3)
    click_rate = round(random.uniform(0.01, 0.03), 3)
    conversion_rate = round(random.uniform(0.005, 0.01), 3)
    
    performance_score = round(
        (open_rate * 0.4) + (click_rate * 0.3) + (conversion_rate * 0.3),
        3
    )
    
    return {
        "open_rate": open_rate,
        "click_rate": click_rate,
        "conversion_rate": conversion_rate,
        "performance_score": performance_score
    }


async def _update_campaign_performance(conn, campaign: Campaign, metrics: Dict[str, float]):
    """Update campaign with generated performance metrics"""
    update_data = {
        'open_rate': metrics['open_rate'],
        'click_rate': metrics['click_rate'],
        'conversion_rate': metrics['conversion_rate'],
        'performance_score': metrics['performance_score'],
        'performance_timestamp': datetime.utcnow().isoformat()
    }
    
    await campaign.update(conn, **update_data)

