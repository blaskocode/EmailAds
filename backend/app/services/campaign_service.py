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
    conn=None,
    assets_s3_path: Optional[str] = None,
    **kwargs
) -> Campaign:
    """
    Create a new campaign in the database
    
    Args:
        campaign_name: Name of the campaign
        advertiser_name: Name of the advertiser
        conn: Database connection (optional, will use db.conn if not provided)
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
    
    # Use provided connection or ensure database connection exists
    # Always use db.conn to ensure we have a valid connection
    if not hasattr(db, 'conn') or db.conn is None:
        await db.connect()
    
    # Try to save, reconnect if connection fails
    try:
        await campaign.save(db.conn)
    except (ValueError, AttributeError) as e:
        error_msg = str(e).lower()
        if "no active connection" in error_msg or "connection is closed" in error_msg or "closed" in error_msg:
            # Connection was closed, reconnect and try again
            logger.warning(f"Database connection was closed, reconnecting... Error: {e}")
            await db.connect()
            await campaign.save(db.conn)
        else:
            raise
    logger.info(f"Created campaign: {campaign.id} - {campaign_name}")
    
    return campaign


async def get_campaign(campaign_id: str, conn=None) -> Optional[Campaign]:
    """
    Get campaign by ID
    
    Args:
        campaign_id: Campaign ID
        conn: Database connection (optional, will use db.conn if not provided)
        
    Returns:
        Campaign object or None if not found
    """
    # Use provided connection or ensure database connection exists
    if conn is None:
        if not hasattr(db, 'conn') or db.conn is None:
            await db.connect()
        conn = db.conn
    
    return await Campaign.get_by_id(conn, campaign_id)


async def update_campaign_assets(
    campaign_id: str,
    assets_s3_path: str,
    asset_metadata: Optional[Dict[str, Any]] = None,
    campaign_name: Optional[str] = None,
    advertiser_name: Optional[str] = None,
    conn=None
) -> Optional[Campaign]:
    """
    Update campaign assets S3 path and optionally update campaign metadata
    
    Args:
        campaign_id: Campaign ID
        assets_s3_path: S3 path to assets
        asset_metadata: Additional asset metadata
        campaign_name: Optional campaign name to update
        advertiser_name: Optional advertiser name to update
        conn: Database connection (optional, will use db.conn if not provided)
        
    Returns:
        Updated Campaign object or None if not found
    """
    campaign = await get_campaign(campaign_id, conn=conn)
    if not campaign:
        return None
    
    # Use provided connection or ensure database connection exists
    if conn is None:
        if not hasattr(db, 'conn') or db.conn is None:
            await db.connect()
        conn = db.conn
    
    # Build update dict with all fields to update
    update_fields = {
        'assets_s3_path': assets_s3_path,
        'ai_processing_data': asset_metadata or {},
        'status': 'uploaded',
        'proof_s3_path': None,  # Clear old proof
        'html_s3_path': None,   # Clear old HTML
        'approved_at': None     # Clear approval timestamp
    }
    
    # Add campaign name and advertiser name if provided
    if campaign_name is not None:
        update_fields['campaign_name'] = campaign_name
    if advertiser_name is not None:
        update_fields['advertiser_name'] = advertiser_name
    
    # When resubmitting, clear old proof and HTML paths, and reset status
    await campaign.update(conn, **update_fields)
    
    logger.info(f"Updated campaign assets: {campaign_id}")
    return campaign

