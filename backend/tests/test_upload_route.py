"""
Tests for upload route
"""
import pytest
from httpx import AsyncClient
from io import BytesIO


@pytest.mark.asyncio
@pytest.mark.integration
async def test_upload_endpoint_missing_fields(client: AsyncClient):
    """Test upload endpoint with missing required fields"""
    # Create a mock image file
    image_data = b'\x89PNG\r\n\x1a\n' + b'0' * 100
    
    files = {
        "logo": ("logo.png", BytesIO(image_data), "image/png")
    }
    
    data = {
        "campaign_name": "Test Campaign"
        # Missing other required fields
    }
    
    response = await client.post("/api/v1/upload", files=files, data=data)
    # Should return validation error
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_upload_endpoint_invalid_file_type(client: AsyncClient):
    """Test upload endpoint with invalid file type"""
    # Create a text file instead of image
    text_data = b"This is not an image"
    
    files = {
        "logo": ("logo.txt", BytesIO(text_data), "text/plain")
    }
    
    data = {
        "campaign_name": "Test Campaign",
        "advertiser_name": "Test Advertiser",
        "subject_line": "Test Subject",
        "preview_text": "Test Preview",
        "body_copy": "Test Body"
    }
    
    response = await client.post("/api/v1/upload", files=files, data=data)
    # Should return validation error for invalid file type
    assert response.status_code in [400, 422]

