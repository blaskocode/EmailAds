# HiBid Automated Email Advertising Workflow System - MVP PRD

**Version:** 1.0 MVP  
**Target Completion:** 36 hours  
**Project ID:** HiBid-Email-MVP-001  
**Date:** November 11, 2025

---

## Executive Summary

This MVP delivers a focused, end-to-end automated email advertising workflow that validates the core value proposition: reducing campaign setup from hours to minutes through AI-powered asset extraction and proof generation. The system handles asset upload, AI-driven content processing, real-time preview, and simple approval workflow.

### MVP Success Criteria
- ✅ Complete advertiser journey in <10 minutes (upload → preview → approve)
- ✅ Sub-5-second proof generation (hard requirement)
- ✅ AI extraction of assets with 80%+ accuracy
- ✅ Production-ready HTML email output
- ✅ Responsive preview (desktop + mobile)

---

## Problem Statement (MVP Scope)

Current HiBid email campaign setup requires:
- Manual collection of assets from advertisers
- Hours of manual template population
- Multiple back-and-forth communications
- Slow approval cycles

**MVP Solution:** Automate the entire flow from asset submission to approved email HTML in minutes, not hours.

---

## User Personas (MVP)

### Primary: Self-Service Advertiser
- **Goal:** Submit campaign assets and get approval-ready email proof quickly
- **Pain Point:** Current process takes hours/days with multiple manual touchpoints
- **MVP Success:** Can complete entire flow independently in <10 minutes

### Secondary: Campaign Manager (Future)
- **Out of MVP Scope:** Multi-campaign management, scheduling, batch operations
- **MVP Note:** System generates output compatible with existing campaign deployment tools

---

## Core User Journey (MVP)

```
1. UPLOAD ASSETS
   ↓ User uploads logo, images, and provides text content
   ↓ AI extracts and structures data automatically
   
2. AI PROCESSING (<5 sec)
   ↓ Content optimization suggestions
   ↓ Email template population
   ↓ Proof generation
   
3. REAL-TIME PREVIEW
   ↓ Desktop + Mobile views
   ↓ Side-by-side comparison
   ↓ Instant regeneration if changes needed
   
4. APPROVE/REJECT
   ↓ Simple binary decision
   ↓ Download production-ready HTML
   ✓ DONE
```

---

## Functional Requirements

### P0: Must-Have (MVP Core)

#### 1. Asset Upload Interface
- **Web form** with drag-and-drop file upload
- **Supported formats:**
  - Images: PNG, JPG, JPEG (max 5MB each)
  - Logo: 1 file required
  - Hero images: 1-3 files
  - Text content: Paste directly or upload TXT/DOCX
- **Fields:**
  - Campaign name
  - Advertiser name
  - Email subject line
  - Preview text
  - Body copy
  - CTA button text
  - CTA button URL
  - Footer text (optional)

#### 2. AI Asset Extraction & Processing
- **Logo extraction:** Detect logo from uploads, auto-resize to template specs
- **Image processing:** 
  - Auto-crop to email-safe dimensions
  - Optimize file size (target <150KB per image)
  - Generate alt text using GPT-4 Vision
- **Content extraction:** 
  - Parse text from uploaded documents
  - Structure into headline, body, CTA sections
- **Content optimization:**
  - Subject line suggestions (3 variations)
  - Preview text optimization for 50-90 chars
  - Body copy formatting (bullet points, short paragraphs)
- **Performance:** Complete extraction + optimization in <3 seconds

#### 3. Email Proof Generation (<5 sec)
- **Template engine:** Single responsive HTML template
- **Auto-population:** Inject extracted assets into template
- **Rendering:** Generate full HTML + inline CSS
- **Preview assets:** Store generated proof for preview system
- **Output:** Production-ready HTML with all assets embedded/linked

#### 4. Real-Time Preview System
- **Desktop preview:** 600px wide email view
- **Mobile preview:** 320px wide responsive view
- **Side-by-side comparison:** Show both views simultaneously
- **Image handling:** Display actual uploaded images
- **Interaction:** 
  - Hover to see full-size images
  - Click to regenerate with changes
  - Instant preview updates (<1 sec)

#### 5. Simple Approval Workflow
- **Binary decision:** Approve or Reject buttons
- **Approve action:**
  - Generate final production HTML
  - Provide download link
  - Store approved version (SQLite)
  - Show success confirmation
- **Reject action:**
  - Allow user to edit assets
  - Return to upload interface with pre-filled data
  - Maintain all previous uploads

#### 6. Production HTML Export
- **Format:** Self-contained HTML file
- **CSS:** All styles inlined for email client compatibility
- **Images:** 
  - Option 1: Base64 encoded (self-contained)
  - Option 2: External URLs (requires S3 public access)
- **Compatibility:** Tested rendering in major email clients
- **Filename:** `{campaign_name}_{timestamp}_approved.html`

### P1: Should-Have (Time Permitting)

#### 7. Edit & Regenerate
- **After preview:** Allow inline text edits
- **Re-upload images:** Replace individual images without full re-upload
- **Instant regeneration:** Update preview in real-time

#### 8. Campaign History
- **Simple list view:** Show last 10 campaigns
- **Metadata:** Campaign name, timestamp, status
- **Actions:** Re-download HTML, view preview

### P2: Nice-to-Have (Post-MVP)

- Multiple template options
- A/B test variation generation
- Scheduled sending integration
- Analytics preview
- Multi-user accounts

---

## Non-Functional Requirements

### Performance
- **Proof generation:** <5 seconds (hard requirement)
- **Asset upload:** <10 seconds for 5MB total
- **Preview rendering:** <1 second
- **API response time:** <500ms (95th percentile)
- **Concurrent users:** Support 10+ simultaneous uploads (MVP scale)

### Security
- **No authentication:** Open access for MVP
- **Input validation:** File type/size checking
- **Sanitization:** Clean user-provided HTML/text
- **S3 security:** Private bucket with signed URLs
- **API rate limiting:** 100 requests/hour per IP

### Scalability (MVP)
- **Database:** SQLite (sufficient for MVP, easy migration path)
- **File storage:** AWS S3
- **Compute:** Single FastAPI instance (horizontal scaling ready)
- **Expected load:** 10-50 campaigns per day

### Reliability
- **Uptime target:** 95% (MVP)
- **Error handling:** Graceful degradation with user-friendly messages
- **Data persistence:** All uploads/proofs stored for 30 days

### Usability
- **Zero training required:** Self-explanatory UI
- **Mobile-friendly:** Responsive web interface
- **Accessibility:** Basic WCAG 2.1 Level A compliance
- **Browser support:** Chrome, Firefox, Safari, Edge (latest 2 versions)

---

## Technical Architecture

### Tech Stack

#### Frontend
- **Framework:** React 18 + Vite
- **UI Library:** Tailwind CSS for rapid development
- **State Management:** React Context (sufficient for MVP)
- **File Upload:** react-dropzone
- **HTTP Client:** Axios

#### Backend
- **Framework:** FastAPI (Python 3.11+)
- **AI Integration:** 
  - OpenAI GPT-4 API (text processing)
  - GPT-4 Vision API (image analysis)
- **Image Processing:** Pillow (Python)
- **Email Template:** MJML → HTML conversion
- **Database:** SQLite3 (local file)
- **File Storage:** AWS S3 (boto3)

#### Infrastructure
- **Deployment:** Docker containers
- **Hosting:** AWS ECS or EC2 (existing infrastructure)
- **CDN:** CloudFront for static assets (optional)
- **Environment:** Single environment (no staging for MVP)

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND (React)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ Upload Page  │→ │ Preview Page │→ │  Results  │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└────────────┬────────────────────────────────────────┘
             │ HTTPS/REST
             ↓
┌────────────────────────────────────────────────────┐
│              BACKEND (FastAPI)                     │
│  ┌──────────────────────────────────────────────┐ │
│  │         API Endpoints                        │ │
│  │  /upload  /process  /preview  /approve      │ │
│  └────┬─────────────┬──────────────┬───────────┘ │
│       ↓             ↓              ↓             │
│  ┌─────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Upload  │  │    AI    │  │   Template    │  │
│  │ Handler │  │ Processor│  │   Generator   │  │
│  └────┬────┘  └────┬─────┘  └───────┬───────┘  │
└───────┼────────────┼────────────────┼───────────┘
        ↓            ↓                ↓
   ┌────────┐  ┌──────────┐    ┌──────────┐
   │   S3   │  │  OpenAI  │    │  SQLite  │
   │ Bucket │  │   API    │    │    DB    │
   └────────┘  └──────────┘    └──────────┘
```

### Data Models

#### Campaign (SQLite)
```python
class Campaign:
    id: UUID
    campaign_name: str
    advertiser_name: str
    status: str  # 'draft', 'approved', 'rejected'
    created_at: datetime
    approved_at: datetime | None
    assets_s3_path: str
    html_s3_path: str | None
```

#### Assets (JSON stored in S3)
```json
{
  "logo_url": "s3://...",
  "hero_images": ["s3://...", "s3://..."],
  "content": {
    "subject_line": "...",
    "preview_text": "...",
    "headline": "...",
    "body_copy": "...",
    "cta_text": "...",
    "cta_url": "...",
    "footer_text": "..."
  },
  "ai_suggestions": {
    "subject_lines": ["...", "...", "..."],
    "optimized_preview": "...",
    "image_alt_texts": ["...", "..."]
  }
}
```

### API Endpoints

#### POST /api/upload
Upload assets and initiate campaign
```json
Request: multipart/form-data
{
  "campaign_name": "Fall Sale 2025",
  "advertiser_name": "Acme Corp",
  "logo": <file>,
  "hero_images": [<file>, <file>],
  "subject_line": "...",
  "body_copy": "...",
  ...
}

Response: 201
{
  "campaign_id": "uuid",
  "status": "processing"
}
```

#### POST /api/process/{campaign_id}
Trigger AI processing and proof generation
```json
Response: 200
{
  "campaign_id": "uuid",
  "status": "ready",
  "preview_url": "/api/preview/{campaign_id}",
  "processing_time_ms": 4231
}
```

#### GET /api/preview/{campaign_id}
Get preview data
```json
Response: 200
{
  "campaign_id": "uuid",
  "html_preview": "<html>...",
  "assets": { ... },
  "ai_suggestions": { ... }
}
```

#### POST /api/approve/{campaign_id}
Approve campaign and generate final HTML
```json
Request: 
{
  "decision": "approve"  // or "reject"
}

Response: 200
{
  "campaign_id": "uuid",
  "status": "approved",
  "download_url": "s3://..."
}
```

---

## Email Template Specification

### Single Responsive Template

**Layout Structure:**
```
┌─────────────────────────────────────┐
│           HEADER / LOGO             │  ← Logo (max height 80px)
├─────────────────────────────────────┤
│                                     │
│         HERO IMAGE                  │  ← Full-width hero
│                                     │
├─────────────────────────────────────┤
│          HEADLINE TEXT              │  ← H1, centered
├─────────────────────────────────────┤
│                                     │
│         BODY COPY                   │  ← Max 3 paragraphs
│                                     │
├─────────────────────────────────────┤
│         [CTA BUTTON]                │  ← Prominent, centered
├─────────────────────────────────────┤
│     Optional: 2-3 Product Images    │  ← Grid layout
├─────────────────────────────────────┤
│          FOOTER                     │  ← Small text, links
└─────────────────────────────────────┘
```

**Specifications:**
- **Width:** 600px (desktop), 100% (mobile)
- **Fonts:** System fonts (Arial, Helvetica, sans-serif)
- **Colors:** Customizable primary/secondary via template vars
- **Images:** Auto-sized, responsive
- **CTA Button:** 
  - Min-width: 200px
  - Height: 44px (touch-friendly)
  - Border-radius: 4px
  - Hover state: Darker shade
- **Responsive breakpoints:** <480px mobile optimization

**Email Client Compatibility:**
- Gmail (web, iOS, Android)
- Outlook (web, desktop)
- Apple Mail
- Yahoo Mail
- Basic rendering in others

---

## AI Processing Specifications

### OpenAI API Usage

#### Text Processing (GPT-4)
**Prompt Template:**
```
You are an email marketing expert. Extract and optimize the following campaign content:

INPUT:
Subject: {user_subject}
Body: {user_body}

TASKS:
1. Generate 3 subject line variations (max 50 chars each)
2. Create preview text (50-90 chars) that complements subject
3. Structure body copy into:
   - Headline (5-10 words)
   - Body (2-3 short paragraphs, max 150 words total)
   - CTA text (2-4 words)
4. Suggest improvements for clarity and urgency

OUTPUT FORMAT: JSON
{
  "subject_lines": ["...", "...", "..."],
  "preview_text": "...",
  "headline": "...",
  "body_paragraphs": ["...", "..."],
  "cta_text": "...",
  "suggestions": "..."
}
```

**Parameters:**
- Model: `gpt-4-turbo-preview`
- Temperature: 0.7
- Max tokens: 800
- Response format: JSON

#### Image Analysis (GPT-4 Vision)
**Prompt Template:**
```
Analyze this image for use in an email marketing campaign.

TASKS:
1. Generate descriptive alt text (max 125 chars)
2. Identify if image contains text (yes/no)
3. Assess image quality (good/fair/poor)
4. Suggest cropping if needed

OUTPUT FORMAT: JSON
{
  "alt_text": "...",
  "contains_text": boolean,
  "quality": "good",
  "crop_suggestion": null
}
```

**Parameters:**
- Model: `gpt-4-vision-preview`
- Max tokens: 300
- Image resolution: Downscaled to 512px max dimension for API

### AI Processing Pipeline

```
1. Upload Complete
   ↓
2. Parallel Processing:
   ├─→ [Text Analysis] → GPT-4 → Optimized content
   ├─→ [Logo Analysis] → GPT-4V → Alt text
   ├─→ [Hero Analysis] → GPT-4V → Alt text + crop
   └─→ [Image Optimization] → Pillow → Resized files
   ↓ (All complete in <3 sec)
3. Aggregate Results
   ↓
4. Populate Template
   ↓
5. Generate HTML Proof
   ↓ (<2 sec)
6. Preview Ready
   TOTAL: <5 seconds
```

### Error Handling
- **AI timeout:** Fallback to basic content (no optimization)
- **Image processing failure:** Use original with warning
- **JSON parse error:** Retry once, then manual fallback
- **All failures logged** for debugging

---

## Development Workflow

### Phase 1: Foundation (Hours 0-8)
- ✅ Project setup (Docker, Git, dependencies)
- ✅ Backend API skeleton (FastAPI)
- ✅ Frontend scaffolding (React + Vite)
- ✅ S3 bucket setup
- ✅ SQLite database initialization
- ✅ Basic upload endpoint working

### Phase 2: Core Features (Hours 8-20)
- ✅ File upload UI with drag-drop
- ✅ AI processing integration (OpenAI)
- ✅ Image processing pipeline
- ✅ Email template creation (MJML)
- ✅ Template population logic
- ✅ Preview generation system

### Phase 3: Preview & Approval (Hours 20-28)
- ✅ Preview UI (desktop + mobile)
- ✅ Real-time preview rendering
- ✅ Approve/reject workflow
- ✅ HTML export functionality
- ✅ Download mechanism

### Phase 4: Polish & Testing (Hours 28-36)
- ✅ Error handling
- ✅ Loading states & UX feedback
- ✅ Input validation
- ✅ End-to-end testing
- ✅ Performance optimization
- ✅ Documentation
- ✅ Deployment preparation

---

## Testing Strategy (MVP)

### Manual Testing Checklist
- [ ] Upload 5 different campaign assets
- [ ] Verify AI extraction accuracy
- [ ] Check proof generation <5 sec
- [ ] Test desktop preview rendering
- [ ] Test mobile preview rendering
- [ ] Approve campaign → download HTML
- [ ] Reject campaign → edit → re-approve
- [ ] Test with oversized images
- [ ] Test with minimal content
- [ ] Test with long body copy

### Performance Validation
- [ ] Measure proof generation time (target: <5 sec)
- [ ] Measure API response times (<500ms)
- [ ] Test concurrent uploads (10 users)
- [ ] Monitor S3 upload speeds

### Browser Compatibility
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

---

## Success Metrics (MVP)

### Primary KPIs
1. **Proof generation time:** <5 seconds (100% of requests)
2. **End-to-end completion time:** <10 minutes (average)
3. **AI extraction accuracy:** >80% (manual validation)
4. **System availability:** >95%

### Secondary Metrics
1. **User error rate:** <10% (failed uploads/approvals)
2. **Re-generation rate:** <30% (users regenerating proofs)
3. **HTML quality:** 100% valid HTML output

---

## Known Limitations (MVP)

### Explicit Trade-offs
- ❌ **No user authentication:** Open access
- ❌ **No multi-user collaboration:** Single user per campaign
- ❌ **No campaign scheduling:** Manual deployment
- ❌ **No email sending:** Export HTML only
- ❌ **Single template:** No customization
- ❌ **No analytics:** No performance tracking
- ❌ **Limited storage:** 30-day retention

### Future Enhancements (Post-MVP)
- User authentication & roles
- Multiple template options
- Campaign scheduling system
- Direct ESP integration (SendGrid, etc.)
- A/B testing capabilities
- Performance analytics
- Unlimited storage
- Batch campaign processing
- Advanced content editing
- Version history

---

## Deployment Strategy

### MVP Deployment
- **Environment:** Single production instance
- **Infrastructure:** Docker container on AWS EC2/ECS
- **Database:** SQLite file on EBS volume
- **Storage:** S3 bucket (us-east-1)
- **Domain:** Subdomain or IP address (no custom domain required)
- **SSL:** Let's Encrypt or AWS Certificate Manager

### Configuration
```bash
# Environment variables
OPENAI_API_KEY=sk-...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET_NAME=hibid-email-assets-mvp
DATABASE_URL=sqlite:///./campaigns.db
FRONTEND_URL=http://localhost:3000
```

### Docker Compose Setup
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./data:/app/data
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

---

## Timeline & Milestones

### 36-Hour Breakdown

**Day 1 (0-12 hours):**
- Hour 0-2: Setup & planning
- Hour 2-6: Backend foundation + S3 integration
- Hour 6-10: Frontend upload UI
- Hour 10-12: Basic upload → storage flow working

**Day 2 (12-24 hours):**
- Hour 12-16: AI processing integration
- Hour 16-20: Email template + generation
- Hour 20-24: Preview UI initial version

**Day 3 (24-36 hours):**
- Hour 24-28: Approval workflow + download
- Hour 28-32: Testing & bug fixes
- Hour 32-36: Polish, documentation, deployment

### Go/No-Go Decision Points
- **Hour 12:** Basic upload working → Continue
- **Hour 24:** AI + preview working → Continue
- **Hour 32:** Full flow working → Final polish

---

## Risk Assessment

### High-Priority Risks
1. **AI processing time >5 seconds**
   - Mitigation: Parallel processing, async operations
   - Fallback: Extend to 7-8 seconds if necessary

2. **OpenAI API rate limits**
   - Mitigation: Request rate limit increase
   - Fallback: Queue system with user notification

3. **Image processing bottleneck**
   - Mitigation: Optimize Pillow operations
   - Fallback: Async processing with progress indicator

### Medium-Priority Risks
1. **S3 upload failures**
   - Mitigation: Retry logic with exponential backoff
   
2. **Template rendering issues**
   - Mitigation: Extensive testing, fallback to basic HTML

3. **Browser compatibility problems**
   - Mitigation: Polyfills, tested in 4 major browsers

---

## Appendix

### Glossary
- **Proof:** Preview version of email for approval
- **Asset:** Logo, image, or text content for campaign
- **CTA:** Call-to-action button/link
- **ESP:** Email service provider
- **MJML:** Email template framework

### References
- OpenAI API Documentation: https://platform.openai.com/docs
- MJML Documentation: https://mjml.io/documentation
- FastAPI Documentation: https://fastapi.tiangolo.com
- React Documentation: https://react.dev

### Contact & Support
- **Project Owner:** [Your Name]
- **Technical Lead:** [Your Name]
- **Deployment Support:** AWS existing team

---

**Document Status:** APPROVED for 36-hour MVP development  
**Last Updated:** November 11, 2025  
**Next Review:** Post-MVP delivery
