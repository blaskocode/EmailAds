"""
Generate endpoint for proof generation
"""
from fastapi import APIRouter, HTTPException, Depends
import logging
import time

from app.models.schemas import PreviewResponse, PromptGenerateRequest, PromptGenerateResponse
from app.services.proof_service import generate_proof, update_campaign_with_proof
from app.services.campaign_service import get_campaign
from app.services.ai_service import generate_campaign_from_prompt
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate/{campaign_id}", response_model=PreviewResponse)
async def generate_campaign_proof(
    campaign_id: str,
    conn = Depends(get_db)
):
    """
    Generate email proof for a processed campaign
    
    This endpoint:
    1. Fetches campaign data and AI processing results
    2. Generates HTML email using template service
    3. Uploads proof to S3
    4. Updates campaign status to 'ready'
    5. Returns preview data
    
    Target: Complete in <2 seconds
    """
    start_time = time.time()
    
    try:
        # Get campaign
        campaign = await get_campaign(campaign_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Generate proof
        proof_result = await generate_proof(campaign_id, campaign)
        
        # Update campaign with proof URL and set status to 'ready'
        await update_campaign_with_proof(
            campaign_id,
            proof_result['proof_s3_url'],
            conn
        )
        
        total_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            f"Proof generation completed for campaign {campaign_id} in {total_time_ms}ms"
        )
        
        # Return preview response
        preview_data = proof_result['preview_data']
        return PreviewResponse(
            campaign_id=campaign_id,
            html_preview=preview_data['html_preview'],
            assets=preview_data['assets'],
            ai_suggestions=preview_data['ai_suggestions'],
            metadata=preview_data['metadata']
        )
        
    except ValueError as e:
        logger.warning(f"Validation error generating proof: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating proof for campaign {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate proof: {str(e)}"
        )


@router.post("/campaigns/{campaign_id}/regenerate", response_model=PreviewResponse)
async def regenerate_campaign_proof(
    campaign_id: str,
    conn = Depends(get_db)
):
    """
    Regenerate email proof for a campaign with updated content/images
    
    This endpoint:
    1. Fetches latest campaign data (including any edits)
    2. Regenerates HTML email using template service
    3. Uploads new proof to S3
    4. Updates campaign status to 'ready'
    5. Returns preview data
    
    Target: Complete in <2 seconds
    """
    start_time = time.time()
    
    try:
        # Get campaign
        campaign = await get_campaign(campaign_id, conn=conn)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Clear proof cache to force regeneration
        from app.services.proof_service import _proof_cache
        if campaign_id in _proof_cache:
            del _proof_cache[campaign_id]
        
        # Generate proof (will use latest campaign data)
        proof_result = await generate_proof(campaign_id, campaign, use_cache=False)
        
        # Update campaign with proof URL and set status to 'ready'
        await update_campaign_with_proof(
            campaign_id,
            proof_result['proof_s3_url'],
            conn
        )
        
        total_time_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            f"Proof regenerated for campaign {campaign_id} in {total_time_ms}ms"
        )
        
        # Return preview response
        preview_data = proof_result['preview_data']
        return PreviewResponse(
            campaign_id=campaign_id,
            html_preview=preview_data['html_preview'],
            assets=preview_data['assets'],
            ai_suggestions=preview_data['ai_suggestions'],
            metadata=preview_data['metadata']
        )
        
    except ValueError as e:
        logger.warning(f"Validation error regenerating proof: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating proof for campaign {campaign_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to regenerate proof: {str(e)}"
        )


@router.post("/campaigns/generate-from-prompt", response_model=PromptGenerateResponse)
async def generate_campaign_from_prompt_endpoint(
    request: PromptGenerateRequest
):
    """
    Generate campaign data from a natural language prompt using AI
    
    This endpoint:
    1. Takes a natural language description of a campaign
    2. Uses GPT-4o-mini to extract structured campaign data
    3. Returns all form fields ready for auto-population
    
    Example prompts:
    - "Create a campaign for Acme Corp's Black Friday sale. 30% off all products. Use code BLACKFRIDAY30."
    - "I need an email campaign for TechStart's new product launch. The product is called CloudSync, a cloud storage solution for businesses."
    """
    try:
        # Validate prompt length
        if not request.prompt or len(request.prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        if len(request.prompt) > 2000:
            raise HTTPException(status_code=400, detail="Prompt exceeds maximum length of 2000 characters")
        
        # Generate campaign data from prompt
        result = await generate_campaign_from_prompt(request.prompt.strip())
        
        logger.info(f"Campaign generated from prompt: {result.get('campaign_name', 'Unknown')}")
        
        # Return structured response
        return PromptGenerateResponse(
            campaign_name=result.get("campaign_name", ""),
            advertiser_name=result.get("advertiser_name", ""),
            subject_line=result.get("subject_line", ""),
            preview_text=result.get("preview_text", ""),
            body_copy=result.get("body_copy", ""),
            cta_text=result.get("cta_text", ""),
            cta_url=result.get("cta_url", "#"),
            footer_text=result.get("footer_text", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating campaign from prompt: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate campaign from prompt: {str(e)}"
        )

