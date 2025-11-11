"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# Request Schemas
class CampaignCreateRequest(BaseModel):
    """Request schema for creating a campaign"""
    campaign_name: str = Field(..., min_length=1, max_length=200)
    advertiser_name: str = Field(..., min_length=1, max_length=200)
    subject_line: Optional[str] = Field(None, max_length=200)
    preview_text: Optional[str] = Field(None, max_length=200)
    body_copy: Optional[str] = Field(None, max_length=5000)
    cta_text: Optional[str] = Field(None, max_length=50)
    cta_url: Optional[str] = Field(None, max_length=500)
    footer_text: Optional[str] = Field(None, max_length=500)


class CampaignUploadResponse(BaseModel):
    """Response schema for campaign upload"""
    campaign_id: str
    status: str
    message: str


class ProcessCampaignRequest(BaseModel):
    """Request schema for processing a campaign"""
    campaign_id: str


class ProcessCampaignResponse(BaseModel):
    """Response schema for campaign processing"""
    campaign_id: str
    status: str
    preview_url: str
    processing_time_ms: int
    ai_suggestions: Optional[dict] = None


class PreviewResponse(BaseModel):
    """Response schema for preview data"""
    campaign_id: str
    html_preview: str
    assets: dict
    ai_suggestions: Optional[dict] = None
    metadata: dict


class ApprovalRequest(BaseModel):
    """Request schema for approval"""
    decision: str = Field(..., pattern="^(approve|reject)$")


class ApprovalResponse(BaseModel):
    """Response schema for approval"""
    campaign_id: str
    status: str
    download_url: Optional[str] = None
    message: str


# Response Schemas
class CampaignResponse(BaseModel):
    """Response schema for campaign data"""
    id: str
    campaign_name: str
    advertiser_name: str
    status: str
    created_at: str
    approved_at: Optional[str] = None
    assets_s3_path: Optional[str] = None
    html_s3_path: Optional[str] = None
    proof_s3_path: Optional[str] = None


class CampaignStatusResponse(BaseModel):
    """Response schema for campaign status check"""
    campaign_id: str
    status: str
    can_preview: bool  # True if status is 'ready' or 'processed'


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    database: Optional[str] = None
    s3: Optional[str] = None

