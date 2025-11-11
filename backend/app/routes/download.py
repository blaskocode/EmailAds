"""
Download endpoint for campaign HTML export
"""
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import StreamingResponse
import logging
from io import BytesIO

from app.services.campaign_service import get_campaign
from app.services.s3_service import s3_service
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/download/{campaign_id}")
async def download_campaign_html(
    campaign_id: str,
    conn = Depends(get_db)
):
    """
    Download campaign HTML file
    
    This endpoint:
    1. Fetches campaign data
    2. Retrieves final HTML from S3
    3. Returns HTML file with proper headers for download
    
    Returns:
        HTML file with Content-Disposition header for download
    """
    try:
        # Get campaign
        campaign = await get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Check if campaign is approved and has HTML
        if campaign.status != 'approved':
            raise HTTPException(
                status_code=400,
                detail=f"Campaign must be approved before download. Current status: {campaign.status}"
            )
        
        if not campaign.html_s3_path:
            raise HTTPException(
                status_code=404,
                detail="Final HTML not found. Please approve the campaign first."
            )
        
        # Extract S3 key from S3 URL
        s3_key = campaign.html_s3_path.replace('s3://', '').split('/', 1)[1] if campaign.html_s3_path.startswith('s3://') else campaign.html_s3_path
        
        # Download HTML from S3 (using boto3 directly for synchronous read)
        import boto3
        from app.config import settings
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        # Get object from S3
        response = s3_client.get_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key
        )
        
        html_content = response['Body'].read().decode('utf-8')
        
        # Generate filename
        from datetime import datetime
        safe_campaign_name = campaign.campaign_name.replace(' ', '_').replace('/', '_')[:50]
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        filename = f"{safe_campaign_name}_{timestamp}.html"
        
        # Create response with proper headers for download
        return Response(
            content=html_content,
            media_type='text/html',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Type': 'text/html; charset=utf-8'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading campaign HTML for {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download HTML: {str(e)}"
        )

