"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
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
    feedback: Optional[str] = Field(None, max_length=2000, description="Optional feedback or comments for the approval decision")


class ApprovalResponse(BaseModel):
    """Response schema for approval"""
    campaign_id: str
    status: str
    download_url: Optional[str] = None
    message: str
    feedback: Optional[str] = None


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
    feedback: Optional[str] = None
    ai_processing_data: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[str] = None
    scheduling_status: Optional[str] = None
    review_status: Optional[str] = None
    reviewer_notes: Optional[str] = None


class CampaignListResponse(BaseModel):
    """Response schema for campaign list"""
    campaigns: List[CampaignResponse]
    total: int
    limit: int
    offset: int
    stats: Optional[Dict[str, int]] = None  # Quick stats by status


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


class CampaignEditRequest(BaseModel):
    """Request schema for editing campaign content"""
    subject_line: Optional[str] = Field(None, max_length=200, description="Updated subject line")
    preview_text: Optional[str] = Field(None, max_length=200, description="Updated preview text")
    body_copy: Optional[str] = Field(None, max_length=5000, description="Updated body copy")
    cta_text: Optional[str] = Field(None, max_length=50, description="Updated CTA text")
    cta_url: Optional[str] = Field(None, max_length=500, description="Updated CTA URL")
    footer_text: Optional[str] = Field(None, max_length=500, description="Updated footer text")
    headline: Optional[str] = Field(None, max_length=200, description="Updated headline")


class CampaignEditResponse(BaseModel):
    """Response schema for campaign edit"""
    campaign_id: str
    message: str
    status: str


class ImageReplaceRequest(BaseModel):
    """Request schema for image replacement (not used, using Form data instead)"""
    image_type: str = Field(..., description="Type: 'logo' or 'hero_{index}'")
    # Note: File upload handled via Form/File, not in this schema


class ImageReplaceResponse(BaseModel):
    """Response schema for image replacement"""
    campaign_id: str
    image_type: str
    image_url: str
    message: str
    status: str


class ScheduleCampaignRequest(BaseModel):
    """Request schema for scheduling a campaign"""
    scheduled_at: str = Field(..., description="ISO 8601 datetime string for when to send the campaign")


class ScheduleCampaignResponse(BaseModel):
    """Response schema for scheduling a campaign"""
    campaign_id: str
    scheduled_at: str
    scheduling_status: str
    message: str


class CancelScheduleResponse(BaseModel):
    """Response schema for canceling a scheduled campaign"""
    campaign_id: str
    message: str
    scheduling_status: Optional[str] = None


class ReviewCampaignRequest(BaseModel):
    """Request schema for reviewing a campaign"""
    review_status: str = Field(..., pattern="^(pending|reviewed|approved|rejected)$", description="Review status: pending, reviewed, approved, or rejected")
    reviewer_notes: Optional[str] = Field(None, max_length=2000, description="Optional notes from the reviewer")


class ReviewCampaignResponse(BaseModel):
    """Response schema for reviewing a campaign"""
    campaign_id: str
    review_status: str
    reviewer_notes: Optional[str] = None
    message: str
