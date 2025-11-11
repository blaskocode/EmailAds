"""
MJML compiler utility for converting MJML to HTML
"""
import subprocess
import tempfile
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def compile_mjml_to_html(mjml_content: str) -> str:
    """
    Compile MJML content to HTML
    
    Args:
        mjml_content: MJML template as string
        
    Returns:
        Compiled HTML string
        
    Raises:
        RuntimeError: If MJML compilation fails
    """
    try:
        # Create temporary file for MJML content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mjml', delete=False) as mjml_file:
            mjml_file.write(mjml_content)
            mjml_path = mjml_file.name
        
        try:
            # Use mjml CLI to compile
            # Try global mjml first, fallback to npx if not available
            try:
                result = subprocess.run(
                    ['mjml', mjml_path, '--config.minify', 'true'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            except FileNotFoundError:
                # Fallback to npx if mjml not found globally
                result = subprocess.run(
                    ['npx', '--yes', 'mjml', mjml_path, '--config.minify', 'true'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                logger.error(f"MJML compilation failed: {error_msg}")
                raise RuntimeError(f"MJML compilation failed: {error_msg}")
            
            # MJML outputs to stdout by default
            html_content = result.stdout
            
            # If stdout is empty, try reading from output file (if --output was used)
            if not html_content:
                html_path = mjml_path.replace('.mjml', '.html')
                if os.path.exists(html_path):
                    with open(html_path, 'r', encoding='utf-8') as html_file:
                        html_content = html_file.read()
                    os.unlink(html_path)
            
            if not html_content:
                raise RuntimeError("MJML compilation produced no output")
            
            return html_content
            
        finally:
            # Clean up temporary MJML file
            if os.path.exists(mjml_path):
                os.unlink(mjml_path)
                
    except subprocess.TimeoutExpired:
        logger.error("MJML compilation timed out")
        raise RuntimeError("MJML compilation timed out")
    except FileNotFoundError:
        logger.error("MJML CLI not found. Please install: npm install -g mjml")
        raise RuntimeError("MJML CLI not found. Please install: npm install -g mjml")
    except Exception as e:
        logger.error(f"Error compiling MJML: {e}")
        raise RuntimeError(f"Error compiling MJML: {str(e)}")


def inline_css(html_content: str) -> str:
    """
    Inline CSS styles in HTML content using premailer
    
    Args:
        html_content: HTML content with external/internal styles
        
    Returns:
        HTML with inlined CSS
    """
    try:
        from premailer import Premailer
        
        p = Premailer(
            html_content,
            strip_important=False,
            keep_style_tags=True,
            remove_classes=False
        )
        inlined_html = p.transform()
        return inlined_html
        
    except ImportError:
        logger.warning("premailer not installed, skipping CSS inlining")
        return html_content
    except Exception as e:
        logger.warning(f"Error inlining CSS: {e}, returning original HTML")
        return html_content

