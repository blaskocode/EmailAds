"""
Tests for validation utilities
"""
import pytest
from io import BytesIO
from fastapi import UploadFile
from app.utils.validators import (
    validate_image_file,
    validate_file_size,
    validate_required_fields
)


@pytest.mark.asyncio
async def test_validate_image_file_valid():
    """Test validation of valid image file"""
    # Create a mock PNG file
    png_data = b'\x89PNG\r\n\x1a\n' + b'0' * 100
    file = UploadFile(
        filename="test.png",
        file=BytesIO(png_data)
    )
    file.content_type = "image/png"
    
    # Should not raise
    result = await validate_image_file(file)
    assert result is True


@pytest.mark.asyncio
async def test_validate_image_file_invalid_type():
    """Test validation rejects invalid file types"""
    file = UploadFile(
        filename="test.txt",
        file=BytesIO(b"not an image")
    )
    file.content_type = "text/plain"
    
    with pytest.raises(Exception):  # Should raise HTTPException
        await validate_image_file(file)


@pytest.mark.asyncio
async def test_validate_file_size_valid():
    """Test validation of file size within limit"""
    # Create a file smaller than 5MB
    small_file = BytesIO(b"x" * (2 * 1024 * 1024))  # 2MB
    file = UploadFile(
        filename="test.jpg",
        file=small_file
    )
    
    # Should not raise
    result = await validate_file_size(file, max_size_mb=5)
    assert result is True


@pytest.mark.asyncio
async def test_validate_file_size_too_large():
    """Test validation rejects files that are too large"""
    # Create a file larger than 5MB
    large_file = BytesIO(b"x" * (6 * 1024 * 1024))  # 6MB
    file = UploadFile(
        filename="test.jpg",
        file=large_file
    )
    
    with pytest.raises(Exception):  # Should raise HTTPException
        await validate_file_size(file, max_size_mb=5)


@pytest.mark.asyncio
async def test_validate_required_fields_all_present():
    """Test validation passes when all required fields are present"""
    data = {
        "campaign_name": "Test Campaign",
        "advertiser_name": "Test Advertiser",
        "subject_line": "Test Subject"
    }
    required = ["campaign_name", "advertiser_name", "subject_line"]
    
    # Should not raise
    result = await validate_required_fields(data, required)
    assert result is True


@pytest.mark.asyncio
async def test_validate_required_fields_missing():
    """Test validation fails when required fields are missing"""
    data = {
        "campaign_name": "Test Campaign"
        # Missing advertiser_name and subject_line
    }
    required = ["campaign_name", "advertiser_name", "subject_line"]
    
    with pytest.raises(Exception):  # Should raise HTTPException
        await validate_required_fields(data, required)

