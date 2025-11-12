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


async def update_campaign_content(
    campaign_id: str,
    edit_request,
    conn=None
) -> Optional[Campaign]:
    """
    Update campaign content fields in ai_processing_data
    
    Args:
        campaign_id: Campaign ID
        edit_request: CampaignEditRequest with fields to update
        conn: Database connection (optional, will use db.conn if not provided)
        
    Returns:
        Updated Campaign object or None if not found
    """
    from app.models.schemas import CampaignEditRequest
    
    campaign = await get_campaign(campaign_id, conn=conn)
    if not campaign:
        return None
    
    # Use provided connection or ensure database connection exists
    if conn is None:
        if not hasattr(db, 'conn') or db.conn is None:
            await db.connect()
        conn = db.conn
    
    # Get current ai_processing_data
    ai_data = campaign.ai_processing_data or {}
    
    # Ensure content structure exists
    if 'content' not in ai_data:
        ai_data['content'] = {}
    
    # Update only provided fields
    edit_dict = edit_request.dict(exclude_unset=True)
    for field, value in edit_dict.items():
        if value is not None:
            ai_data['content'][field] = value
    
    # Also update ai_results if they exist (for consistency)
    if 'ai_results' in ai_data:
        text_opt = ai_data['ai_results'].get('text_optimization', {})
        
        # Update text_optimization fields if they exist in edit request
        if 'subject_line' in edit_dict and edit_dict['subject_line']:
            # Update first subject line in suggestions
            if 'subject_lines' in text_opt and text_opt['subject_lines']:
                text_opt['subject_lines'][0] = edit_dict['subject_line']
            else:
                text_opt['subject_lines'] = [edit_dict['subject_line']]
        
        if 'preview_text' in edit_dict and edit_dict['preview_text']:
            text_opt['preview_text'] = edit_dict['preview_text']
        
        if 'headline' in edit_dict and edit_dict['headline']:
            text_opt['headline'] = edit_dict['headline']
        
        if 'body_copy' in edit_dict and edit_dict['body_copy']:
            # Convert body_copy to paragraphs if it's a string
            if isinstance(edit_dict['body_copy'], str):
                # Split by newlines or create single paragraph
                paragraphs = [p.strip() for p in edit_dict['body_copy'].split('\n') if p.strip()]
                if not paragraphs:
                    paragraphs = [edit_dict['body_copy']]
                text_opt['body_paragraphs'] = paragraphs
            else:
                text_opt['body_paragraphs'] = edit_dict['body_copy']
        
        if 'cta_text' in edit_dict and edit_dict['cta_text']:
            text_opt['cta_text'] = edit_dict['cta_text']
        
        ai_data['ai_results']['text_optimization'] = text_opt
    
    # Update campaign
    await campaign.update(conn, ai_processing_data=ai_data)
    
    logger.info(f"Updated campaign content for {campaign_id}")
    return campaign

