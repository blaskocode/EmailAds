"""
Proof service for generating and storing email proofs
"""
import asyncio
import time
from typing import Dict, Optional
from io import BytesIO
import logging
from datetime import datetime

from app.services.template_service import generate_email_from_campaign
from app.services.s3_service import s3_service
from app.services.campaign_service import get_campaign
from app.services.file_service import generate_s3_key
from app.models.campaign import Campaign

logger = logging.getLogger(__name__)

# Simple in-memory cache for generated proofs (campaign_id -> proof_data)
# In production, consider using Redis or similar
_proof_cache: Dict[str, Dict] = {}


async def generate_proof(
    campaign_id: str,
    campaign_obj: Optional[Campaign] = None,
    use_cache: bool = True
) -> Dict:
    """
    Generate email proof for a campaign
    
    Args:
        campaign_id: Campaign ID
        campaign_obj: Optional campaign object (if already fetched)
        use_cache: Whether to use cached proof if available
        
    Returns:
        Dictionary with proof data including:
        - html_content: Generated HTML
        - proof_s3_url: S3 URL of stored proof
        - preview_data: Preview data structure
        - generation_time_ms: Time taken to generate
    """
    start_time = time.time()
    
    try:
        # Check cache first (if enabled and campaign already has proof)
        if use_cache and campaign_id in _proof_cache:
            cached_proof = _proof_cache[campaign_id]
            logger.info(f"Using cached proof for campaign {campaign_id}")
            return cached_proof
        
        # Fetch campaign if not provided
        if campaign_obj is None:
            campaign_obj = await get_campaign(campaign_id)
            if not campaign_obj:
                raise ValueError(f"Campaign {campaign_id} not found")
        
        # Check if campaign has been processed
        if campaign_obj.status != 'processed' and campaign_obj.status != 'ready':
            raise ValueError(
                f"Campaign {campaign_id} must be processed before generating proof. "
                f"Current status: {campaign_obj.status}"
            )
        
        # Check if AI results exist
        ai_results = campaign_obj.ai_processing_data.get('ai_results') if campaign_obj.ai_processing_data else None
        if not ai_results:
            raise ValueError(f"Campaign {campaign_id} has no AI processing results")
        
        # Generate HTML email using template service
        html_content = await generate_email_from_campaign(
            campaign_id,
            campaign_obj,
            ai_results
        )
        
        # Upload proof HTML to S3
        proof_s3_key = generate_s3_key(campaign_id, 'proof.html', 'proofs')
        html_file_obj = BytesIO(html_content.encode('utf-8'))
        proof_s3_url = await s3_service.upload_file(
            html_file_obj,
            proof_s3_key,
            content_type='text/html'
        )
        
        # Prepare preview data structure
        text_opt = ai_results.get('text_optimization', {})
        image_analysis = ai_results.get('image_analysis', {})
        optimized_images = ai_results.get('optimized_images', {})
        
        # Extract subject lines (use first one as primary)
        subject_lines = text_opt.get('subject_lines', [])
        primary_subject = subject_lines[0] if subject_lines else None
        
        # Get preview text
        preview_text = text_opt.get('preview_text') or ''
        
        # Prepare image URLs (convert S3 URLs to presigned URLs for preview)
        # Helper function to extract S3 key from S3 URL
        def extract_s3_key(s3_url: str) -> Optional[str]:
            """Extract S3 key from s3://bucket/key format"""
            if not s3_url or not s3_url.startswith('s3://'):
                return None
            parts = s3_url.replace('s3://', '').split('/', 1)
            return parts[1] if len(parts) == 2 else None
        
        # Generate presigned URLs in parallel for better performance
        image_url_tasks = []
        image_urls = {}
        
        # Logo URL task
        if optimized_images.get('logo'):
            logo_key = extract_s3_key(optimized_images['logo'])
            if logo_key:
                image_url_tasks.append(('logo', s3_service.get_presigned_url(logo_key, expiration=3600)))
        
        # Hero image URL tasks
        hero_url_tasks = []
        for idx, hero_s3_url in enumerate(optimized_images.get('hero_images', [])):
            if hero_s3_url:
                hero_key = extract_s3_key(hero_s3_url)
                if hero_key:
                    hero_url_tasks.append((idx, s3_service.get_presigned_url(hero_key, expiration=3600)))
        
        # Execute all presigned URL generation in parallel
        all_tasks = image_url_tasks + hero_url_tasks
        if all_tasks:
            results = await asyncio.gather(*[task[1] for task in all_tasks], return_exceptions=True)
            
            # Process logo result
            if image_url_tasks:
                logo_result = results[0]
                if not isinstance(logo_result, Exception):
                    image_urls['logo'] = logo_result
                result_idx = 1
            else:
                result_idx = 0
            
            # Process hero image results
            hero_urls = []
            for idx, (original_idx, _) in enumerate(hero_url_tasks):
                hero_result = results[result_idx + idx]
                if not isinstance(hero_result, Exception):
                    hero_urls.append(hero_result)
            image_urls['hero_images'] = hero_urls
        
        preview_data = {
            'campaign_id': campaign_id,
            'html_preview': html_content,
            'assets': {
                'logo_url': image_urls.get('logo'),
                'hero_image_urls': image_urls.get('hero_images', [])
            },
            'ai_suggestions': {
                'subject_lines': subject_lines,
                'preview_text': preview_text,
                'headline': text_opt.get('headline'),
                'body_paragraphs': text_opt.get('body_paragraphs', []),
                'cta_text': text_opt.get('cta_text'),
                'image_alt_texts': {
                    'logo': image_analysis.get('logo', {}).get('alt_text') if image_analysis.get('logo') else None,
                    'hero_images': [
                        hero.get('alt_text') for hero in image_analysis.get('hero_images', [])
                    ]
                },
                'suggestions': text_opt.get('suggestions')
            },
            'metadata': {
                'campaign_name': campaign_obj.campaign_name,
                'advertiser_name': campaign_obj.advertiser_name,
                'subject_line': primary_subject,
                'preview_text': preview_text,
                'generated_at': datetime.utcnow().isoformat(),
                'proof_s3_url': proof_s3_url
            }
        }
        
        generation_time_ms = int((time.time() - start_time) * 1000)
        
        result = {
            'html_content': html_content,
            'proof_s3_url': proof_s3_url,
            'preview_data': preview_data,
            'generation_time_ms': generation_time_ms
        }
        
        # Cache the result for future requests
        if use_cache:
            _proof_cache[campaign_id] = result
        
        logger.info(
            f"Proof generated for campaign {campaign_id} in {generation_time_ms}ms. "
            f"Proof stored at: {proof_s3_url}"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating proof for campaign {campaign_id}: {e}", exc_info=True)
        raise


async def update_campaign_with_proof(
    campaign_id: str,
    proof_s3_url: str,
    conn
) -> Optional[Campaign]:
    """
    Update campaign with proof S3 URL and set status to 'ready'
    
    Args:
        campaign_id: Campaign ID
        proof_s3_url: S3 URL of the proof
        conn: Database connection
        
    Returns:
        Updated Campaign object
    """
    try:
        campaign = await get_campaign(campaign_id)
        if not campaign:
            return None
        
        await campaign.update(
            conn,
            proof_s3_path=proof_s3_url,
            status='ready'
        )
        
        logger.info(f"Campaign {campaign_id} updated with proof URL and status set to 'ready'")
        return campaign
        
    except Exception as e:
        logger.error(f"Error updating campaign with proof: {e}", exc_info=True)
        raise

