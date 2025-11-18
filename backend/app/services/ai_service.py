"""
AI service for OpenAI GPT-4 and GPT-4 Vision integration
"""
from openai import OpenAI
from typing import Dict, List, Optional, Any
import json
import asyncio
import logging
from app.config import settings
from app.utils.image_utils import prepare_image_for_vision_api, convert_to_base64

logger = logging.getLogger(__name__)

# Lazy initialization of OpenAI client to avoid import-time errors
_client = None

def get_openai_client():
    """Get or create OpenAI client instance"""
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


async def process_text_content(
    subject_line: Optional[str],
    body_copy: Optional[str],
    cta_text: Optional[str] = None
) -> Dict:
    """
    Process text content with GPT-4 to generate optimized email content
    
    Args:
        subject_line: Original subject line
        body_copy: Original body copy
        cta_text: Original CTA text
        
    Returns:
        Dictionary with optimized content
    """
    try:
        prompt = f"""You are an email marketing expert. Extract and optimize the following campaign content:

INPUT:
Subject: {subject_line or 'Not provided'}
Body: {body_copy or 'Not provided'}
CTA: {cta_text or 'Not provided'}

TASKS:
1. Generate 3 subject line variations (max 50 chars each)
2. Create preview text (50-90 chars) that complements the best subject line
3. Structure body copy into:
   - Headline (5-10 words, compelling and clear)
   - Body (2-3 short paragraphs, max 150 words total)
   - CTA text (2-4 words, action-oriented)
4. Suggest improvements for clarity and urgency

OUTPUT FORMAT: JSON only, no markdown, no code blocks
{{
  "subject_lines": ["variation 1", "variation 2", "variation 3"],
  "preview_text": "preview text here",
  "headline": "compelling headline",
  "body_paragraphs": ["paragraph 1", "paragraph 2"],
  "cta_text": "action text",
  "suggestions": "brief improvement suggestions"
}}"""

        # Run in thread pool since OpenAI client is synchronous
        # Using gpt-4o for better performance and cost
        client = get_openai_client()
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an email marketing expert. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        
        logger.info("Text content processed successfully")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in text processing: {e}")
        # Fallback to basic structure
        return {
            "subject_lines": [subject_line or "Email Campaign"] * 3,
            "preview_text": "Check out our latest offer!" if not subject_line else subject_line[:90],
            "headline": "Special Offer" if not body_copy else body_copy.split('.')[0][:50],
            "body_paragraphs": [body_copy or "Thank you for your interest."],
            "cta_text": cta_text or "Learn More",
            "suggestions": "Content processed with fallback"
        }
    except Exception as e:
        logger.error(f"Error processing text content: {e}")
        raise


async def analyze_image(image_bytes: bytes, image_type: str = "image") -> Dict:
    """
    Analyze image with GPT-4 Vision to generate alt text and assessment
    
    Args:
        image_bytes: Image as bytes
        image_type: Type of image (logo, hero, etc.)
        
    Returns:
        Dictionary with analysis results
    """
    try:
        # Prepare image for API (downscale to 512px max)
        prepared_image = prepare_image_for_vision_api(image_bytes)
        base64_image = convert_to_base64(prepared_image)
        
        prompt = f"""Analyze this {image_type} for use in an email marketing campaign.

TASKS:
1. Generate descriptive alt text (max 125 chars, be specific about what's in the image)
2. Identify if image contains text (true/false)
3. Assess image quality (good/fair/poor)
4. Suggest cropping if needed (null if no cropping needed, or brief description)

OUTPUT FORMAT: JSON only, no markdown, no code blocks
{{
  "alt_text": "descriptive alt text",
  "contains_text": true,
  "quality": "good",
  "crop_suggestion": null
}}"""

        # Run in thread pool
        # Using gpt-4o which supports vision
        client = get_openai_client()
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=300
        )
        
        content = response.choices[0].message.content
        
        # Try to extract JSON from response
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise
        
        logger.info(f"Image analysis completed for {image_type}")
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        # Fallback alt text
        return {
            "alt_text": f"{image_type.capitalize()} image",
            "contains_text": False,
            "quality": "fair",
            "crop_suggestion": None
        }


async def process_images_parallel(
    logo_bytes: Optional[bytes],
    hero_images_bytes: List[bytes]
) -> Dict:
    """
    Process multiple images in parallel with GPT-4 Vision
    
    Args:
        logo_bytes: Logo image bytes
        hero_images_bytes: List of hero image bytes
        
    Returns:
        Dictionary with analysis results for all images
    """
    tasks = []
    
    # Add logo analysis if present
    if logo_bytes:
        tasks.append(analyze_image(logo_bytes, "logo"))
    
    # Add hero image analyses
    for idx, hero_bytes in enumerate(hero_images_bytes):
        tasks.append(analyze_image(hero_bytes, f"hero image {idx + 1}"))
    
    # Process all images in parallel
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results
        logo_analysis = None
        hero_analyses = []
        
        result_idx = 0
        if logo_bytes:
            if isinstance(results[result_idx], Exception):
                logger.error(f"Logo analysis failed: {results[result_idx]}")
                logo_analysis = {
                    "alt_text": "Company logo",
                    "contains_text": False,
                    "quality": "fair",
                    "crop_suggestion": None
                }
            else:
                logo_analysis = results[result_idx]
            result_idx += 1
        
        for idx in range(len(hero_images_bytes)):
            if isinstance(results[result_idx], Exception):
                logger.error(f"Hero image {idx + 1} analysis failed: {results[result_idx]}")
                hero_analyses.append({
                    "alt_text": f"Hero image {idx + 1}",
                    "contains_text": False,
                    "quality": "fair",
                    "crop_suggestion": None
                })
            else:
                hero_analyses.append(results[result_idx])
            result_idx += 1
        
        return {
            "logo": logo_analysis,
            "hero_images": hero_analyses
        }
    
    return {"logo": None, "hero_images": []}


async def process_text_content_with_history(
    subject_line: Optional[str],
    body_copy: Optional[str],
    cta_text: Optional[str] = None,
    historical_examples: Optional[List[Dict[str, Any]]] = None
) -> Dict:
    """
    Process text content with GPT-4 using historical high-performing examples as context
    
    Args:
        subject_line: Original subject line
        body_copy: Original body copy
        cta_text: Original CTA text
        historical_examples: List of high-performing campaign examples
        
    Returns:
        Dictionary with optimized content aligned with proven patterns
    """
    try:
        # Build historical context if available
        historical_context = ""
        if historical_examples and len(historical_examples) > 0:
            historical_context = "\n\nHIGH-PERFORMING EXAMPLES FROM PAST CAMPAIGNS:\n"
            for idx, example in enumerate(historical_examples[:5], 1):  # Top 5 examples
                historical_context += f"\nExample {idx} (Performance Score: {example.get('performance_score', 0):.2f}):\n"
                if example.get('subject_line'):
                    historical_context += f"  Subject: {example['subject_line']}\n"
                if example.get('preview_text'):
                    historical_context += f"  Preview: {example['preview_text']}\n"
                if example.get('cta_text'):
                    historical_context += f"  CTA: {example['cta_text']}\n"
            historical_context += "\nUse these patterns as inspiration while creating fresh, unique content.\n"
        
        prompt = f"""You are an email marketing expert. Extract and optimize the following campaign content:{historical_context}

INPUT:
Subject: {subject_line or 'Not provided'}
Body: {body_copy or 'Not provided'}
CTA: {cta_text or 'Not provided'}

TASKS:
1. Generate 3 subject line variations (max 50 chars each) that align with proven high-performing patterns
2. Create preview text (50-90 chars) that complements the best subject line
3. Structure body copy into:
   - Headline (5-10 words, compelling and clear)
   - Body (2-3 short paragraphs, max 150 words total)
   - CTA text (2-4 words, action-oriented, similar to high-performing examples)
4. Suggest improvements for clarity and urgency

OUTPUT FORMAT: JSON only, no markdown, no code blocks
{{
  "subject_lines": ["variation 1", "variation 2", "variation 3"],
  "preview_text": "preview text here",
  "headline": "compelling headline",
  "body_paragraphs": ["paragraph 1", "paragraph 2"],
  "cta_text": "action text",
  "suggestions": "brief improvement suggestions"
}}"""

        # Run in thread pool since OpenAI client is synchronous
        client = get_openai_client()
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an email marketing expert. Always respond with valid JSON only. Use historical examples as inspiration but create fresh, unique content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        
        logger.info("Text content processed with historical context successfully")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in text processing with history: {e}")
        # Fallback to basic structure
        return {
            "subject_lines": [subject_line or "Email Campaign"] * 3,
            "preview_text": "Check out our latest offer!" if not subject_line else subject_line[:90],
            "headline": "Special Offer" if not body_copy else body_copy.split('.')[0][:50],
            "body_paragraphs": [body_copy or "Thank you for your interest."],
            "cta_text": cta_text or "Learn More",
            "suggestions": "Content processed with fallback"
        }
    except Exception as e:
        logger.error(f"Error processing text content with history: {e}")
        raise


async def generate_campaign_from_prompt(prompt: str) -> Dict[str, Any]:
    """
    Generate campaign data from a natural language prompt using GPT-4o-mini
    
    Args:
        prompt: Natural language description of the campaign
        
    Returns:
        Dictionary with extracted campaign fields:
        - campaign_name
        - advertiser_name
        - subject_line
        - preview_text
        - body_copy
        - cta_text
        - cta_url
        - footer_text
    """
    try:
        system_prompt = """You are an email marketing expert. Extract campaign information from user prompts and return structured JSON data. Always respond with valid JSON only, no markdown, no code blocks."""
        
        user_prompt = f"""You are an email marketing expert. Extract campaign information from the following user prompt:

USER PROMPT:
{prompt}

TASKS:
1. Extract or infer campaign name (if not provided, suggest one based on context)
2. Extract or infer advertiser/company name
3. Generate compelling subject line (max 50 chars)
4. Generate preview text (50-90 chars) that complements subject line
5. Structure body copy:
   - Headline (5-10 words, compelling)
   - Body paragraphs (2-3 paragraphs, max 150 words total)
   - Combine headline and paragraphs into a single body_copy string
6. Generate CTA text (2-4 words, action-oriented)
7. Extract or suggest CTA URL (if mentioned, or use placeholder like "#" or "https://example.com")
8. Generate footer text (optional, company info or disclaimer)

OUTPUT FORMAT: JSON only, no markdown, no code blocks
{{
  "campaign_name": "...",
  "advertiser_name": "...",
  "subject_line": "...",
  "preview_text": "...",
  "body_copy": "...",
  "cta_text": "...",
  "cta_url": "...",
  "footer_text": "..."
}}"""

        # Run in thread pool since OpenAI client is synchronous
        # Using gpt-4o-mini for faster response and lower cost
        client = get_openai_client()
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # Validate and ensure all required fields exist
        required_fields = ["campaign_name", "advertiser_name", "subject_line", "preview_text", "body_copy", "cta_text", "cta_url"]
        for field in required_fields:
            if field not in result or not result[field]:
                if field == "cta_url":
                    result[field] = "#"
                elif field == "footer_text":
                    result[field] = ""
                else:
                    # Provide sensible defaults
                    if field == "campaign_name":
                        result[field] = "Email Campaign"
                    elif field == "advertiser_name":
                        result[field] = "Company"
                    elif field == "subject_line":
                        result[field] = "Special Offer"
                    elif field == "preview_text":
                        result[field] = "Check out our latest offer!"
                    elif field == "body_copy":
                        result[field] = "Thank you for your interest in our products."
                    elif field == "cta_text":
                        result[field] = "Learn More"
        
        # Ensure footer_text exists (optional field)
        if "footer_text" not in result:
            result["footer_text"] = ""
        
        logger.info(f"Campaign generated from prompt successfully. Campaign: {result.get('campaign_name', 'Unknown')}")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in prompt generation: {e}")
        # Fallback to basic structure based on prompt
        fallback_name = prompt[:50] if len(prompt) > 0 else "Email Campaign"
        return {
            "campaign_name": fallback_name,
            "advertiser_name": "Company",
            "subject_line": "Special Offer",
            "preview_text": "Check out our latest offer!",
            "body_copy": prompt[:500] if len(prompt) > 0 else "Thank you for your interest.",
            "cta_text": "Learn More",
            "cta_url": "#",
            "footer_text": ""
        }
    except Exception as e:
        logger.error(f"Error generating campaign from prompt: {e}", exc_info=True)
        raise

