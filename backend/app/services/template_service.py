"""
Email template service for generating HTML emails from templates
"""
from typing import Dict, Optional, List
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.utils.mjml_compiler import compile_mjml_to_html, inline_css
from app.services.s3_service import s3_service

logger = logging.getLogger(__name__)

# Get templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True
)


async def get_presigned_url_from_s3_url(s3_url: str) -> Optional[str]:
    """
    Convert S3 URL (s3://bucket/key) to presigned URL
    
    Args:
        s3_url: S3 URL in format s3://bucket/key
        
    Returns:
        Presigned URL or None if conversion fails
    """
    try:
        if not s3_url or not s3_url.startswith('s3://'):
            return s3_url  # Return as-is if not an S3 URL
        
        # Extract bucket and key from s3://bucket/key
        parts = s3_url.replace('s3://', '').split('/', 1)
        if len(parts) != 2:
            logger.warning(f"Invalid S3 URL format: {s3_url}")
            return None
        
        bucket, key = parts
        
        # Generate presigned URL (1 hour expiration)
        presigned_url = await s3_service.get_presigned_url(key, expiration=3600)
        return presigned_url
        
    except Exception as e:
        logger.error(f"Error generating presigned URL for {s3_url}: {e}")
        return None


async def generate_email_html(
    campaign_data: Dict,
    ai_results: Optional[Dict] = None
) -> str:
    """
    Generate HTML email from template with campaign and AI data
    
    Args:
        campaign_data: Campaign data dictionary with:
            - campaign_name
            - advertiser_name
            - subject_line (optional)
            - preview_text (optional)
            - body_copy (optional)
            - cta_text (optional)
            - cta_url (optional)
            - footer_text (optional)
        ai_results: AI processing results with:
            - text_optimization: {subject_lines, preview_text, headline, body_paragraphs, cta_text}
            - image_analysis: {logo: {alt_text}, hero_images: [{alt_text}]}
            - optimized_images: {logo: s3_url, hero_images: [s3_urls]}
        
    Returns:
        Compiled HTML email string
    """
    try:
        # Load MJML template
        template = env.get_template('email_template.mjml')
        
        # Extract AI-optimized content (prefer AI over original)
        text_opt = ai_results.get('text_optimization', {}) if ai_results else {}
        image_analysis = ai_results.get('image_analysis', {}) if ai_results else {}
        optimized_images = ai_results.get('optimized_images', {}) if ai_results else {}
        
        # Prepare template variables
        template_vars = {
            'campaign_name': campaign_data.get('campaign_name', 'Email Campaign'),
            'advertiser_name': campaign_data.get('advertiser_name', ''),
            
            # Preview text (AI optimized or original)
            'preview_text': text_opt.get('preview_text') or campaign_data.get('preview_text') or '',
            
            # Headline (AI optimized or from body copy)
            'headline': text_opt.get('headline') or campaign_data.get('headline') or '',
            
            # Body paragraphs (AI optimized or original)
            'body_paragraphs': text_opt.get('body_paragraphs') or (
                [campaign_data.get('body_copy')] if campaign_data.get('body_copy') else []
            ),
            
            # CTA (AI optimized or original)
            'cta_text': text_opt.get('cta_text') or campaign_data.get('cta_text') or 'Learn More',
            'cta_url': campaign_data.get('cta_url') or '#',
            
            # Footer
            'footer_text': campaign_data.get('footer_text') or '',
        }
        
        # Handle logo
        logo_s3_url = optimized_images.get('logo')
        if logo_s3_url:
            logo_url = await get_presigned_url_from_s3_url(logo_s3_url)
            template_vars['logo_url'] = logo_url
            logo_analysis = image_analysis.get('logo', {})
            template_vars['logo_alt_text'] = logo_analysis.get('alt_text', 'Company logo')
        else:
            template_vars['logo_url'] = None
            template_vars['logo_alt_text'] = ''
        
        # Handle hero image (use first one)
        hero_s3_urls = optimized_images.get('hero_images', [])
        if hero_s3_urls and len(hero_s3_urls) > 0:
            hero_url = await get_presigned_url_from_s3_url(hero_s3_urls[0])
            template_vars['hero_image_url'] = hero_url
            hero_analyses = image_analysis.get('hero_images', [])
            if hero_analyses and len(hero_analyses) > 0:
                template_vars['hero_alt_text'] = hero_analyses[0].get('alt_text', 'Hero image')
            else:
                template_vars['hero_alt_text'] = 'Hero image'
        else:
            template_vars['hero_image_url'] = None
            template_vars['hero_alt_text'] = ''
        
        # Handle product images (additional hero images)
        if hero_s3_urls and len(hero_s3_urls) > 1:
            product_images = []
            hero_analyses = image_analysis.get('hero_images', [])
            for idx, hero_s3_url in enumerate(hero_s3_urls[1:4]):  # Max 3 product images
                product_url = await get_presigned_url_from_s3_url(hero_s3_url)
                hero_idx = idx + 1  # Skip first hero image
                alt_text = 'Product image'
                if hero_analyses and hero_idx < len(hero_analyses):
                    alt_text = hero_analyses[hero_idx].get('alt_text', 'Product image')
                product_images.append({
                    'url': product_url,
                    'alt_text': alt_text
                })
            template_vars['product_images'] = product_images if product_images else None
        else:
            template_vars['product_images'] = None
        
        # Render MJML template with variables
        mjml_content = template.render(**template_vars)
        
        # Compile MJML to HTML
        html_content = compile_mjml_to_html(mjml_content)
        
        # Inline CSS for email client compatibility
        final_html = inline_css(html_content)
        
        logger.info(f"Email HTML generated successfully for campaign: {campaign_data.get('campaign_name')}")
        return final_html
        
    except Exception as e:
        logger.error(f"Error generating email HTML: {e}", exc_info=True)
        raise


async def generate_email_from_campaign(
    campaign_id: str,
    campaign_obj,
    ai_results: Optional[Dict] = None
) -> str:
    """
    Generate email HTML from campaign object
    
    Args:
        campaign_id: Campaign ID
        campaign_obj: Campaign model object
        ai_results: Optional AI results (if None, will extract from campaign.ai_processing_data)
        
    Returns:
        Compiled HTML email string
    """
    # Extract AI results from campaign if not provided
    if ai_results is None:
        ai_results = campaign_obj.ai_processing_data.get('ai_results') if campaign_obj.ai_processing_data else None
    
    # Prepare campaign data
    campaign_data = {
        'campaign_name': campaign_obj.campaign_name,
        'advertiser_name': campaign_obj.advertiser_name,
        'subject_line': None,  # Will be extracted from ai_processing_data if needed
        'preview_text': None,
        'body_copy': None,
        'cta_text': None,
        'cta_url': None,
        'footer_text': None,
    }
    
    # Extract original content from ai_processing_data if available
    original_content = campaign_obj.ai_processing_data.get('content', {}) if campaign_obj.ai_processing_data else {}
    campaign_data.update({
        'subject_line': original_content.get('subject_line'),
        'preview_text': original_content.get('preview_text'),
        'body_copy': original_content.get('body_copy'),
        'cta_text': original_content.get('cta_text'),
        'cta_url': original_content.get('cta_url'),
        'footer_text': original_content.get('footer_text'),
    })
    
    return await generate_email_html(campaign_data, ai_results)

