"""
Campaign service for database operations
"""
from app.models.campaign import Campaign
from app.database import db
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


async def create_campaign(
    campaign_name: str,
    advertiser_name: str,
    assets_s3_path: Optional[str] = None,
    **kwargs
) -> Campaign:
    """
    Create a new campaign in the database
    
    Args:
        campaign_name: Name of the campaign
        advertiser_name: Name of the advertiser
        assets_s3_path: S3 path to assets
        **kwargs: Additional campaign fields
        
    Returns:
        Created Campaign object
    """
    campaign = Campaign(
        campaign_name=campaign_name,
        advertiser_name=advertiser_name,
        status='draft',
        assets_s3_path=assets_s3_path,
        **kwargs
    )
    
    # Ensure database connection
    if not hasattr(db, 'conn') or db.conn is None:
        await db.connect()
    
    await campaign.save(db.conn)
    logger.info(f"Created campaign: {campaign.id} - {campaign_name}")
    
    return campaign


async def get_campaign(campaign_id: str) -> Optional[Campaign]:
    """
    Get campaign by ID
    
    Args:
        campaign_id: Campaign ID
        
    Returns:
        Campaign object or None if not found
    """
    if not hasattr(db, 'conn') or db.conn is None:
        await db.connect()
    
    return await Campaign.get_by_id(db.conn, campaign_id)


async def update_campaign_assets(
    campaign_id: str,
    assets_s3_path: str,
    asset_metadata: Optional[Dict[str, Any]] = None
) -> Optional[Campaign]:
    """
    Update campaign assets S3 path
    
    Args:
        campaign_id: Campaign ID
        assets_s3_path: S3 path to assets
        asset_metadata: Additional asset metadata
        
    Returns:
        Updated Campaign object or None if not found
    """
    campaign = await get_campaign(campaign_id)
    if not campaign:
        return None
    
    if not hasattr(db, 'conn') or db.conn is None:
        await db.connect()
    
    await campaign.update(
        db.conn,
        assets_s3_path=assets_s3_path,
        ai_processing_data=asset_metadata or {}
    )
    
    logger.info(f"Updated campaign assets: {campaign_id}")
    return campaign

