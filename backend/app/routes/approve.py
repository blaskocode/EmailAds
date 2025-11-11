"""
Approval endpoint for campaign approval/rejection
"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import logging
from io import BytesIO

from app.models.schemas import ApprovalRequest, ApprovalResponse
from app.services.campaign_service import get_campaign
from app.services.proof_service import generate_proof
from app.services.template_service import generate_email_from_campaign
from app.services.s3_service import s3_service
from app.services.file_service import generate_s3_key
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/approve/{campaign_id}", response_model=ApprovalResponse)
async def approve_campaign(
    campaign_id: str,
    request: ApprovalRequest,
    conn = Depends(get_db)
):
    """
    Approve or reject a campaign
    
    If approved:
    1. Generate final production HTML
    2. Upload to S3
    3. Update campaign status to 'approved'
    4. Store approval timestamp
    5. Return download URL
    
    If rejected:
    1. Update campaign status to 'rejected'
    2. Return message
    """
    try:
        # Get campaign
        campaign = await get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        if request.decision == 'approve':
            # Generate final HTML (production-ready)
            ai_results = campaign.ai_processing_data.get('ai_results') if campaign.ai_processing_data else None
            if not ai_results:
                raise HTTPException(
                    status_code=400,
                    detail="Campaign must be processed before approval"
                )
            
            # Generate final HTML using template service
            final_html = await generate_email_from_campaign(
                campaign_id,
                campaign,
                ai_results
            )
            
            # Upload final HTML to S3
            final_html_key = generate_s3_key(campaign_id, 'final.html', 'html')
            html_file_obj = BytesIO(final_html.encode('utf-8'))
            final_html_s3_url = await s3_service.upload_file(
                html_file_obj,
                final_html_key,
                content_type='text/html'
            )
            
            # Generate presigned URL for download (24 hour expiration)
            download_url = await s3_service.get_presigned_url(
                final_html_key,
                expiration=86400  # 24 hours
            )
            
            # Update campaign status and feedback
            campaign.status = 'approved'
            campaign.approved_at = datetime.utcnow().isoformat()
            campaign.html_s3_path = final_html_s3_url
            campaign.feedback = request.feedback
            
            await campaign.update(
                conn,
                status='approved',
                approved_at=campaign.approved_at,
                html_s3_path=final_html_s3_url,
                feedback=request.feedback
            )
            
            logger.info(f"Campaign {campaign_id} approved. Final HTML stored at: {final_html_s3_url}")
            if request.feedback:
                logger.info(f"Feedback provided: {request.feedback[:100]}...")
            
            return ApprovalResponse(
                campaign_id=campaign_id,
                status='approved',
                download_url=download_url,
                message="Campaign approved successfully. Final HTML is ready for download.",
                feedback=request.feedback
            )
        
        elif request.decision == 'reject':
            # Update campaign status to rejected and store feedback
            campaign.status = 'rejected'
            campaign.feedback = request.feedback
            
            await campaign.update(
                conn,
                status='rejected',
                feedback=request.feedback
            )
            
            logger.info(f"Campaign {campaign_id} rejected")
            if request.feedback:
                logger.info(f"Rejection feedback: {request.feedback[:100]}...")
            
            return ApprovalResponse(
                campaign_id=campaign_id,
                status='rejected',
                download_url=None,
                message="Campaign rejected. You can edit and resubmit.",
                feedback=request.feedback
            )
        
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid decision. Must be 'approve' or 'reject'"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing approval for campaign {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process approval: {str(e)}"
        )

