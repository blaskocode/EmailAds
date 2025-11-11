# HiBid Email MVP - API Documentation

**Base URL:** `http://localhost:8000/api/v1`  
**API Version:** 1.0.0  
**Documentation:** Interactive API docs available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

---

## Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
   - [Health Check](#health-check)
   - [Upload Campaign](#upload-campaign)
   - [Process Campaign](#process-campaign)
   - [Generate Proof](#generate-proof)
   - [Get Preview](#get-preview)
   - [Approve Campaign](#approve-campaign)
   - [Download HTML](#download-html)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [Rate Limits](#rate-limits)

---

## Authentication

**Note:** Authentication is not required for MVP. All endpoints are publicly accessible.

---

## Endpoints

### Health Check

Check API health and service status.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "hibid-email-mvp",
  "database": "connected",
  "s3": "connected"
}
```

**Status Codes:**
- `200 OK` - Service is healthy
- `200 OK` (status: "degraded") - Service is running but some dependencies are unavailable

---

### Upload Campaign

Upload campaign assets and create a new campaign record.

**Endpoint:** `POST /upload`

**Content-Type:** `multipart/form-data`

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `campaign_name` | string | Yes | Campaign name (1-200 chars) |
| `advertiser_name` | string | Yes | Advertiser name (1-200 chars) |
| `logo` | file | Yes | Logo image file (PNG, JPG, JPEG, max 5MB) |
| `hero_images` | file[] | No | Hero image files (1-3 files, PNG, JPG, JPEG, max 5MB each) |
| `subject_line` | string | No | Email subject line (max 200 chars) |
| `preview_text` | string | No | Email preview text (max 200 chars) |
| `body_copy` | string | No | Email body copy (max 5000 chars) |
| `cta_text` | string | No | Call-to-action button text (max 50 chars) |
| `cta_url` | string | No | Call-to-action URL (max 500 chars) |
| `footer_text` | string | No | Footer text (max 500 chars) |

**Response:**
```json
{
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "uploaded",
  "message": "Campaign created successfully"
}
```

**Status Codes:**
- `200 OK` - Campaign created successfully
- `400 Bad Request` - Invalid file type or size
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "campaign_name=Summer Sale" \
  -F "advertiser_name=Acme Corp" \
  -F "logo=@logo.png" \
  -F "hero_images=@hero1.jpg" \
  -F "subject_line=Summer Sale - 50% Off" \
  -F "body_copy=Don't miss our amazing summer sale!"
```

---

### Process Campaign

Process campaign with AI: optimize content and images.

**Endpoint:** `POST /process/{campaign_id}`

**Path Parameters:**
- `campaign_id` (string, required) - Campaign UUID

**Response:**
```json
{
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processed",
  "processing_time_ms": 3200,
  "ai_results": {
    "subject_variations": [
      "Summer Sale - 50% Off Everything!",
      "Don't Miss Our Summer Sale - 50% Off",
      "Limited Time: 50% Off Summer Sale"
    ],
    "preview_text": "Get 50% off all items during our summer sale",
    "body_copy": "Don't miss our amazing summer sale! Get 50% off all items...",
    "cta_text": "Shop Now",
    "image_alt_texts": {
      "logo": "Acme Corp logo",
      "hero_1": "Summer sale banner with 50% off text"
    }
  },
  "optimized_images": {
    "logo": "https://s3.amazonaws.com/bucket/campaign_id/logo_optimized.png",
    "hero_1": "https://s3.amazonaws.com/bucket/campaign_id/hero_1_optimized.jpg"
  }
}
```

**Status Codes:**
- `200 OK` - Processing completed successfully
- `400 Bad Request` - Campaign assets not found or invalid state
- `404 Not Found` - Campaign not found
- `500 Internal Server Error` - Processing failed

**Performance:** Target completion time <5 seconds

---

### Generate Proof

Generate email proof for a processed campaign.

**Endpoint:** `POST /generate/{campaign_id}`

**Path Parameters:**
- `campaign_id` (string, required) - Campaign UUID

**Response:**
```json
{
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "html_preview": "<!DOCTYPE html>...",
  "assets": {
    "logo_url": "https://s3.amazonaws.com/bucket/logo.png",
    "hero_images": [
      "https://s3.amazonaws.com/bucket/hero_1.jpg"
    ]
  },
  "ai_suggestions": {
    "subject_variations": ["..."],
    "preview_text": "...",
    "body_copy": "..."
  },
  "metadata": {
    "campaign_name": "Summer Sale",
    "advertiser_name": "Acme Corp",
    "generated_at": "2025-11-11T12:00:00Z"
  }
}
```

**Status Codes:**
- `200 OK` - Proof generated successfully
- `400 Bad Request` - Campaign not processed or invalid state
- `404 Not Found` - Campaign not found
- `500 Internal Server Error` - Generation failed

**Performance:** Target completion time <2 seconds

---

### Get Preview

Get preview data for a campaign (generates proof if needed).

**Endpoint:** `GET /preview/{campaign_id}`

**Path Parameters:**
- `campaign_id` (string, required) - Campaign UUID

**Response:**
```json
{
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "html_preview": "<!DOCTYPE html>...",
  "assets": {
    "logo_url": "https://s3.amazonaws.com/bucket/logo.png",
    "hero_images": ["..."]
  },
  "ai_suggestions": {
    "subject_variations": ["..."],
    "preview_text": "...",
    "body_copy": "..."
  },
  "metadata": {
    "campaign_name": "Summer Sale",
    "advertiser_name": "Acme Corp",
    "generated_at": "2025-11-11T12:00:00Z"
  }
}
```

**Status Codes:**
- `200 OK` - Preview data retrieved successfully
- `400 Bad Request` - Campaign not processed
- `404 Not Found` - Campaign not found
- `500 Internal Server Error` - Preview generation failed

**Note:** If campaign status is 'ready', uses cached proof. If 'processed', generates proof first.

---

### Approve Campaign

Approve or reject a campaign.

**Endpoint:** `POST /approve/{campaign_id}`

**Path Parameters:**
- `campaign_id` (string, required) - Campaign UUID

**Request Body:**
```json
{
  "decision": "approve"  // or "reject"
}
```

**Response (Approved):**
```json
{
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "approved",
  "download_url": "https://s3.amazonaws.com/bucket/final.html?signature=...",
  "message": "Campaign approved successfully. Final HTML is ready for download."
}
```

**Response (Rejected):**
```json
{
  "campaign_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "rejected",
  "download_url": null,
  "message": "Campaign rejected. You can edit and resubmit."
}
```

**Status Codes:**
- `200 OK` - Approval/rejection processed successfully
- `400 Bad Request` - Campaign not processed or invalid decision
- `404 Not Found` - Campaign not found
- `500 Internal Server Error` - Processing failed

---

### Download HTML

Download the final approved campaign HTML file.

**Endpoint:** `GET /download/{campaign_id}`

**Path Parameters:**
- `campaign_id` (string, required) - Campaign UUID

**Response:**
- Content-Type: `text/html`
- Content-Disposition: `attachment; filename="CampaignName_20251111.html"`
- Body: HTML file content

**Status Codes:**
- `200 OK` - HTML file downloaded successfully
- `400 Bad Request` - Campaign not approved
- `404 Not Found` - Campaign or HTML file not found
- `500 Internal Server Error` - Download failed

**Example:**
```bash
curl -O -J "http://localhost:8000/api/v1/download/550e8400-e29b-41d4-a716-446655440000"
```

---

## Data Models

### Campaign Status Flow

```
uploaded → processed → ready → approved/rejected
```

**Status Values:**
- `uploaded` - Campaign assets uploaded, ready for processing
- `processed` - AI processing completed, ready for proof generation
- `ready` - Proof generated, ready for approval
- `approved` - Campaign approved, final HTML available
- `rejected` - Campaign rejected, can be edited and resubmitted

### Campaign Model

```json
{
  "campaign_id": "string (UUID)",
  "campaign_name": "string",
  "advertiser_name": "string",
  "status": "uploaded | processed | ready | approved | rejected",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime",
  "approved_at": "ISO 8601 datetime (nullable)",
  "ai_processing_data": {
    "logo": {
      "s3_url": "string",
      "filename": "string",
      "size": "number"
    },
    "hero_images": [
      {
        "s3_url": "string",
        "filename": "string",
        "size": "number"
      }
    ],
    "content": {
      "subject_line": "string",
      "preview_text": "string",
      "body_copy": "string",
      "cta_text": "string",
      "cta_url": "string",
      "footer_text": "string"
    },
    "ai_results": {
      "subject_variations": ["string"],
      "preview_text": "string",
      "body_copy": "string",
      "cta_text": "string",
      "image_alt_texts": {
        "logo": "string",
        "hero_1": "string"
      }
    }
  },
  "proof_s3_path": "string (nullable)",
  "html_s3_path": "string (nullable)"
}
```

---

## Error Handling

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

- `400 Bad Request` - Invalid request parameters or business logic violation
- `404 Not Found` - Resource (campaign, file) not found
- `422 Unprocessable Entity` - Validation error (missing/invalid fields)
- `500 Internal Server Error` - Server error (check logs for details)

### Custom Error Types

The API uses custom exceptions for better error handling:

- `CampaignNotFoundError` - Campaign does not exist
- `CampaignStateError` - Campaign is in invalid state for operation
- `S3Error` - S3 operation failed
- `AIProcessingError` - AI processing failed

---

## Rate Limits

**Note:** Rate limiting is not implemented in MVP. Consider implementing for production.

**Recommended Limits (Production):**
- Upload: 10 requests/minute per IP
- Process: 5 requests/minute per IP
- Generate: 10 requests/minute per IP
- Preview: 20 requests/minute per IP

---

## Testing

### Running Tests

**Backend:**
```bash
cd backend
pytest
pytest --cov=app --cov-report=html
```

**Frontend:**
```bash
cd frontend
npm test
npm run test:coverage
```

### Test Coverage

Target coverage: >60% for MVP

---

## Performance Targets

- **Upload:** <1 second
- **Process:** <5 seconds (hard requirement)
- **Generate:** <2 seconds
- **Preview:** <1 second (cached) or <2 seconds (generate)
- **Approve:** <1 second
- **Download:** <500ms

---

## Support

For issues or questions:
- Check the [README.md](README.md) for setup instructions
- Review [TASK_BREAKDOWN.md](TASK_BREAKDOWN.md) for development details
- Interactive API docs available at `/docs` when server is running

---

**Last Updated:** November 2025  
**API Version:** 1.0.0

