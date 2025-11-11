# HiBid Email MVP - Task Breakdown & Pull Request Plan

**Target Timeline:** 36 hours  
**Development Methodology:** AI-first, rapid iteration  
**Branch Strategy:** Feature branches → main

---

## Development Phases Overview

```
Phase 1: Foundation (0-8h)     → 3 PRs
Phase 2: Core Features (8-20h) → 5 PRs  
Phase 3: UI & Approval (20-28h)→ 3 PRs
Phase 4: Polish (28-36h)       → 2 PRs
Phase 5: Post-MVP (36h+)        → 7 PRs
Phase 6: P1 Features            → 4 PRs
                        TOTAL: 24 PRs
```

---

# PHASE 1: FOUNDATION (Hours 0-8)

## PR #1: Project Setup & Infrastructure
**Branch:** `feature/project-setup`  
**Time Estimate:** 2 hours  
**Dependencies:** None  
**Status:** ✅ Completed

### Tasks
- [x] **1.1** Initialize Git repository
  - Create .gitignore (Python, Node, env files)
  - Set up main branch
  - Create README.md with project overview

- [x] **1.2** Set up project structure
  ```
  hibid-email-mvp/
  ├── backend/
  │   ├── app/
  │   │   ├── __init__.py
  │   │   ├── main.py
  │   │   ├── config.py
  │   │   ├── models/
  │   │   ├── routes/
  │   │   ├── services/
  │   │   └── utils/
  │   ├── requirements.txt
  │   ├── Dockerfile
  │   └── .env.example
  ├── frontend/
  │   ├── src/
  │   │   ├── components/
  │   │   ├── pages/
  │   │   ├── services/
  │   │   └── App.jsx
  │   ├── package.json
  │   ├── vite.config.js
  │   └── Dockerfile
  ├── docker-compose.yml
  └── README.md
  ```

- [x] **1.3** Create Docker configuration
  - Backend Dockerfile (Python 3.11)
  - Frontend Dockerfile (Node 18)
  - docker-compose.yml for local development
  - Health check endpoints

- [x] **1.4** Set up environment variables
  - .env.example template
  - Configuration validation
  - Secret management structure

**Acceptance Criteria:**
- ✅ Docker containers build successfully
- ✅ docker-compose up runs both services
- ✅ Backend returns 200 on /health
- ✅ Frontend loads on localhost:3000

**Files Created:**
- README.md, .gitignore
- docker-compose.yml
- backend/Dockerfile, backend/requirements.txt
- frontend/Dockerfile, frontend/package.json

---

## PR #2: Backend Foundation & Database
**Branch:** `feature/backend-foundation`  
**Time Estimate:** 3 hours  
**Dependencies:** PR #1  
**Status:** ✅ Completed

### Tasks
- [x] **2.1** Install backend dependencies
  ```
  fastapi==0.104.1
  uvicorn[standard]==0.24.0
  python-multipart==0.0.6
  pillow==10.1.0
  boto3==1.29.7
  openai==1.3.7
  python-dotenv==1.0.0
  pydantic==2.5.0
  aiosqlite==0.19.0
  ```

- [x] **2.2** Create FastAPI application structure
  - main.py with CORS middleware
  - config.py with settings (Pydantic BaseSettings)
  - Health check endpoint
  - API versioning (/api/v1/)

- [x] **2.3** Set up SQLite database
  - Create database schema (campaigns table)
  - Database connection manager
  - Async database operations with aiosqlite
  - Migration script (initial schema)

- [x] **2.4** Create data models
  - Pydantic models for request/response
  - SQLAlchemy models for database
  - Campaign model with all fields
  - Asset metadata model

- [x] **2.5** AWS S3 integration setup
  - boto3 client initialization
  - S3 upload utility functions
  - Signed URL generation
  - Bucket configuration validation

**Acceptance Criteria:**
- ✅ FastAPI server runs on port 8000
- ✅ /health endpoint returns 200
- ✅ Database file created on startup
- ✅ S3 connection test passes
- ✅ All models validate correctly

**Files Created:**
- backend/app/main.py
- backend/app/config.py
- backend/app/models/campaign.py
- backend/app/models/schemas.py
- backend/app/database.py
- backend/app/services/s3_service.py

---

## PR #3: Frontend Foundation
**Branch:** `feature/frontend-foundation`  
**Time Estimate:** 3 hours  
**Dependencies:** PR #1  
**Status:** ✅ Completed

### Tasks
- [x] **3.1** Initialize React + Vite project
  ```bash
  npm create vite@latest frontend -- --template react
  cd frontend
  npm install
  ```

- [x] **3.2** Install frontend dependencies
  ```
  axios
  react-router-dom
  react-dropzone
  tailwindcss
  postcss
  autoprefixer
  ```

- [x] **3.3** Configure Tailwind CSS
  - tailwind.config.js
  - postcss.config.js
  - Import Tailwind in index.css

- [x] **3.4** Set up routing
  - React Router configuration
  - Route structure:
    - / → Upload page
    - /preview/:campaignId → Preview page
    - /success/:campaignId → Success page

- [x] **3.5** Create API service layer
  - Axios instance with base URL
  - API methods for all endpoints
  - Error handling wrapper
  - Request/response interceptors

- [x] **3.6** Create basic layout components
  - Header component
  - Footer component
  - Layout wrapper
  - Loading spinner component

**Acceptance Criteria:**
- ✅ Frontend builds without errors
- ✅ Vite dev server runs on port 3000
- ✅ Tailwind CSS styles apply correctly
- ✅ Routing works between pages
- ✅ API service can connect to backend

**Files Created:**
- frontend/src/App.jsx
- frontend/src/main.jsx
- frontend/src/services/api.js
- frontend/src/components/Layout.jsx
- frontend/src/components/Header.jsx
- frontend/src/components/Loading.jsx
- frontend/tailwind.config.js

---

# PHASE 2: CORE FEATURES (Hours 8-20)

## PR #4: File Upload API & Storage
**Branch:** `feature/upload-api`  
**Time Estimate:** 3 hours  
**Dependencies:** PR #2  
**Status:** ✅ Completed

### Tasks
- [x] **4.1** Create upload endpoint
  - POST /api/v1/upload
  - Multipart form data handling
  - File validation (size, type)
  - Generate unique campaign ID

- [x] **4.2** File processing utilities
  - Image validation (PNG, JPG, JPEG)
  - File size checking (max 5MB)
  - Mime type verification
  - Temporary storage handling

- [x] **4.3** S3 upload implementation
  - Upload logo to S3
  - Upload hero images to S3
  - Generate S3 object keys (campaign_id/filename)
  - Store file URLs in database

- [x] **4.4** Campaign creation logic
  - Create campaign record in database
  - Store metadata (name, advertiser, timestamps)
  - Store S3 paths for assets
  - Return campaign ID to client

- [x] **4.5** Error handling
  - File upload failures
  - S3 connection errors
  - Database errors
  - Input validation errors

**Acceptance Criteria:**
- ✅ POST /api/v1/upload accepts files
- ✅ Files uploaded to S3 successfully
- ✅ Campaign created in database
- ✅ Returns campaign_id in response
- ✅ Error responses are user-friendly

**Files Created:**
- backend/app/routes/upload.py
- backend/app/services/file_service.py
- backend/app/services/campaign_service.py
- backend/app/utils/validators.py

---

## PR #5: Upload UI Component
**Branch:** `feature/upload-ui`  
**Time Estimate:** 3 hours  
**Dependencies:** PR #3, PR #4  
**Status:** ✅ Completed

### Tasks
- [x] **5.1** Create upload form component
  - Campaign name input
  - Advertiser name input
  - Subject line input
  - Preview text input
  - Body copy textarea

- [x] **5.2** Implement file upload UI
  - Drag-and-drop zone using react-dropzone
  - Logo upload (single file)
  - Hero images upload (1-3 files)
  - File preview thumbnails
  - Remove file functionality

- [x] **5.3** Form validation
  - Required field checking
  - File size validation
  - File type validation
  - Real-time error messages

- [x] **5.4** Form submission
  - Build FormData object
  - Call upload API
  - Show upload progress
  - Handle success/error states

- [x] **5.5** UX enhancements
  - Loading states during upload
  - Success confirmation
  - Error message display
  - Redirect to preview on success

**Acceptance Criteria:**
- ✅ Form captures all required data
- ✅ Drag-and-drop works for images
- ✅ File previews display correctly
- ✅ Validation prevents invalid submissions
- ✅ Upload progress shown to user
- ✅ Redirects to preview after upload

**Files Created:**
- frontend/src/pages/UploadPage.jsx
- frontend/src/components/FileUpload.jsx
- frontend/src/components/FormInput.jsx
- frontend/src/hooks/useFileUpload.js

---

## PR #6: AI Processing Integration
**Branch:** `feature/ai-processing`  
**Time Estimate:** 4 hours  
**Dependencies:** PR #4  
**Status:** ✅ Completed

### Tasks
- [x] **6.1** OpenAI service setup
  - Initialize OpenAI client
  - API key configuration
  - Error handling for API calls
  - Rate limit management

- [x] **6.2** Text content processing
  - GPT-4 prompt for content optimization
  - Subject line generation (3 variations)
  - Preview text optimization
  - Body copy structuring
  - JSON response parsing

- [x] **6.3** Image analysis with GPT-4 Vision
  - Image-to-base64 conversion
  - Alt text generation for each image
  - Image quality assessment
  - Crop suggestions (if needed)

- [x] **6.4** Image optimization
  - Resize images to email-safe dimensions
  - Logo: max 300x100px
  - Hero: max 600x400px
  - File compression (target <150KB)
  - Format conversion if needed

- [x] **6.5** Process endpoint
  - POST /api/v1/process/{campaign_id}
  - Parallel processing of text and images
  - Aggregate results
  - Store AI outputs in database
  - Return processed data

- [x] **6.6** Performance optimization
  - Async/await for all AI calls
  - Parallel processing with asyncio.gather
  - Timeout handling (10 sec max)
  - Fallback for AI failures

**Acceptance Criteria:**
- ✅ GPT-4 generates content variations
- ✅ GPT-4 Vision creates alt texts
- ✅ Images optimized correctly
- ✅ Total processing time <5 seconds
- ✅ Handles AI API errors gracefully
- ✅ Results stored in database

**Files Created:**
- backend/app/services/ai_service.py
- backend/app/services/image_service.py
- backend/app/routes/process.py
- backend/app/utils/image_utils.py

---

## PR #7: Email Template Engine
**Branch:** `feature/email-template`  
**Time Estimate:** 3 hours  
**Dependencies:** PR #6  
**Status:** ✅ Completed

### Tasks
- [x] **7.1** Create MJML template
  - Responsive email structure
  - Header with logo
  - Hero image section
  - Headline section
  - Body copy section
  - CTA button
  - Footer
  - Mobile optimization

- [x] **7.2** Template variable system
  - Define template variables
  - Variable substitution logic
  - Jinja2 or string templating
  - Safe HTML escaping

- [x] **7.3** HTML generation service
  - MJML to HTML conversion
  - CSS inlining (inline all styles)
  - Image URL injection
  - Production HTML output

- [x] **7.4** Template population
  - Inject campaign content
  - Inject optimized AI content
  - Inject S3 image URLs
  - Generate alt texts

- [x] **7.5** Email client testing
  - Test HTML in Gmail
  - Test in Outlook
  - Test in Apple Mail
  - Mobile rendering verification

**Acceptance Criteria:**
- ✅ MJML template compiles to valid HTML
- ✅ All CSS is inlined
- ✅ Responsive design works (mobile/desktop)
- ✅ Images display correctly
- ✅ Links are clickable
- ✅ Renders well in major email clients

**Files Created:**
- backend/app/templates/email_template.mjml
- backend/app/services/template_service.py
- backend/app/utils/mjml_compiler.py

---

## PR #8: Proof Generation System
**Branch:** `feature/proof-generation`  
**Time Estimate:** 3 hours  
**Dependencies:** PR #7  
**Status:** ✅ Completed

### Tasks
- [x] **8.1** Generate endpoint
  - POST /api/v1/generate/{campaign_id}
  - Fetch campaign data from database
  - Fetch processed AI content
  - Call template service

- [x] **8.2** Proof generation logic
  - Populate template with data
  - Generate HTML proof
  - Create desktop preview
  - Create mobile preview
  - Store proof in S3

- [x] **8.3** Preview data structure
  - HTML content for rendering
  - Metadata (subject, preview text)
  - AI suggestions
  - Image URLs
  - Timestamp

- [x] **8.4** Performance optimization
  - Cache generated proofs
  - Async HTML generation
  - Parallel S3 uploads
  - Total time <2 seconds

- [x] **8.5** Update database
  - Store proof S3 URL
  - Update campaign status to 'ready'
  - Store generation timestamp

**Acceptance Criteria:**
- ✅ Proof generates in <2 seconds
- ✅ HTML is valid and renders correctly
- ✅ Preview data includes all fields
- ✅ Proof stored in S3
- ✅ Database updated with proof URL

**Files Created:**
- backend/app/routes/generate.py
- backend/app/services/proof_service.py

---

# PHASE 3: UI & APPROVAL (Hours 20-28)

## PR #9: Preview UI Component
**Branch:** `feature/preview-ui`  
**Time Estimate:** 4 hours  
**Dependencies:** PR #8, PR #5  
**Status:** ✅ Completed

### Tasks
- [x] **9.1** Preview page layout
  - Two-column layout (desktop + mobile)
  - Desktop preview (600px width)
  - Mobile preview (320px width)
  - Side-by-side comparison

- [x] **9.2** HTML rendering
  - iframe for desktop preview
  - iframe for mobile preview
  - Sandboxed rendering
  - Responsive container

- [x] **9.3** Campaign details panel
  - Show campaign name
  - Show subject line
  - Show preview text
  - Show AI suggestions
  - Editable fields (stretch goal)

- [x] **9.4** Preview controls
  - Toggle desktop/mobile view
  - Fullscreen preview option
  - Refresh preview button
  - Download HTML button (coming in PR #10)

- [x] **9.5** Loading states
  - Skeleton loader while generating
  - Preview loading spinner
  - Error state if generation fails

- [x] **9.6** Fetch preview data
  - GET /api/v1/preview/{campaign_id}
  - Display proof HTML
  - Show metadata
  - Handle loading/error states

**Acceptance Criteria:**
- ✅ Desktop preview renders correctly
- ✅ Mobile preview renders correctly
- ✅ Side-by-side layout works
- ✅ Campaign details display
- ✅ Preview loads from API
- ✅ Loading states work properly

**Files Created:**
- frontend/src/pages/PreviewPage.jsx
- frontend/src/components/PreviewFrame.jsx
- frontend/src/components/CampaignDetails.jsx

---

## PR #10: Approval Workflow
**Branch:** `feature/approval-workflow`  
**Time Estimate:** 3 hours  
**Dependencies:** PR #9, PR #8  
**Status:** ✅ Completed

### Tasks
- [x] **10.1** Approval endpoint
  - POST /api/v1/approve/{campaign_id}
  - Accept decision: 'approve' or 'reject'
  - Update campaign status
  - Generate final HTML if approved

- [x] **10.2** Final HTML generation
  - Create production-ready HTML
  - Inline all CSS
  - Embed or link images (configurable)
  - Upload to S3 with unique name
  - Return download URL

- [x] **10.3** Approval UI buttons
  - Approve button (green, prominent)
  - Reject button (red, secondary)
  - Confirmation modal for approval
  - Loading state during processing

- [x] **10.4** Success page
  - Confirmation message
  - Download button for HTML
  - View preview again option
  - Start new campaign button

- [x] **10.5** Rejection flow
  - Return to upload page
  - Pre-fill form with existing data
  - Allow editing
  - Reprocess from scratch

**Acceptance Criteria:**
- ✅ Approve button generates final HTML
- ✅ Final HTML downloads correctly
- ✅ Reject button returns to upload
- ✅ Success page shows confirmation
- ✅ Database updated with approval status

**Files Created:**
- backend/app/routes/approve.py
- frontend/src/pages/SuccessPage.jsx
- frontend/src/components/ApprovalButtons.jsx

---

## PR #11: Download & Export
**Branch:** `feature/export-html`  
**Time Estimate:** 1 hour  
**Dependencies:** PR #10  
**Status:** ✅ Completed

### Tasks
- [x] **11.1** Download endpoint
  - GET /api/v1/download/{campaign_id}
  - Fetch final HTML from S3
  - Set correct content headers
  - Force download (not preview)

- [x] **11.2** HTML export options
  - Base64 encoded images (self-contained)
  - External image URLs (smaller file)
  - User choice in UI (optional)

- [x] **11.3** Download UI
  - Download button on success page
  - File naming: {campaign_name}_{date}.html
  - Progress indicator
  - Success notification

- [x] **11.4** Alternative: Copy to clipboard
  - Copy HTML to clipboard button
  - Success toast notification

**Acceptance Criteria:**
- ✅ Download triggers browser download
- ✅ File has correct name
- ✅ HTML is valid and complete
- ✅ Works in all major browsers

**Files Created:**
- backend/app/routes/download.py
- frontend/src/utils/downloadHelpers.js

---

# PHASE 4: POLISH & TESTING (Hours 28-36)

## PR #12: Error Handling & Validation
**Branch:** `feature/error-handling`  
**Time Estimate:** 3 hours  
**Dependencies:** All previous PRs  
**Status:** ✅ Completed

### Tasks
- [x] **12.1** Backend error handling
  - Global exception handler
  - Custom error classes
  - User-friendly error messages
  - Error logging

- [x] **12.2** Input validation
  - Pydantic validators for all models
  - File type validation
  - File size validation
  - URL validation
  - Text length limits

- [x] **12.3** Frontend error handling
  - API error interceptor
  - User-friendly error messages
  - Error boundary component
  - Retry logic for failed requests

- [x] **12.4** Loading & feedback states
  - Loading spinners for all async operations
  - Progress indicators
  - Success notifications
  - Error notifications

- [x] **12.5** Edge case handling
  - Network failures
  - API timeouts
  - Large file uploads
  - Missing assets
  - Invalid data

**Acceptance Criteria:**
- ✅ All errors show user-friendly messages
- ✅ No uncaught exceptions
- ✅ Invalid inputs are rejected
- ✅ Loading states appear consistently
- ✅ Retry logic works for transient failures

**Files Created:**
- backend/app/utils/error_handlers.py
- frontend/src/components/ErrorBoundary.jsx
- frontend/src/components/Toast.jsx

---

## PR #13: Testing, Documentation & Deployment
**Branch:** `feature/testing-docs-deploy`  
**Time Estimate:** 5 hours  
**Dependencies:** All previous PRs  
**Status:** ✅ Completed

### Tasks
- [x] **13.1** Backend testing
  - Unit tests for key functions
  - API endpoint tests (pytest)
  - S3 upload test
  - Database operations test
  - AI service mocks

- [x] **13.2** Frontend testing
  - Component rendering tests (Vitest)
  - API service tests
  - Form validation tests
  - User flow tests

- [x] **13.3** Integration testing
  - End-to-end upload flow
  - Preview generation
  - Approval workflow
  - Download functionality

- [x] **13.4** Performance testing
  - Measure proof generation time
  - Test with large images
  - Test concurrent requests
  - Identify bottlenecks

- [x] **13.5** Documentation
  - API documentation (OpenAPI/Swagger)
  - README.md with setup instructions
  - Environment variables documentation
  - Deployment guide
  - User guide

- [x] **13.6** Deployment preparation
  - Production environment variables
  - Docker build optimization
  - Health check endpoints
  - Logging configuration
  - Monitoring setup (basic)

- [x] **13.7** Final deployment
  - Build Docker images
  - Deploy to AWS ECS/EC2
  - Configure S3 bucket
  - Set up database persistence
  - SSL certificate (if applicable)
  - Test production deployment

**Acceptance Criteria:**
- ✅ All tests pass
- ✅ Code coverage >60%
- ✅ Documentation is complete
- ✅ Application deploys successfully
- ✅ Production environment is stable
- ✅ End-to-end flow works in production

**Files Created:**
- backend/tests/
- frontend/tests/
- README.md (comprehensive)
- DEPLOYMENT.md
- API_DOCS.md

---

# Development Best Practices

## Git Workflow
1. Create feature branch from main
2. Make atomic commits with clear messages
3. Write PR description with:
   - What changed
   - Why it changed
   - How to test
4. Self-review before creating PR
5. Merge to main after testing

## Commit Message Format
```
<type>(<scope>): <subject>

<body>

Examples:
feat(upload): add drag-and-drop file upload
fix(api): resolve S3 upload timeout issue
docs(readme): add deployment instructions
```

## Code Quality Checklist
- [ ] Code is readable and well-commented
- [ ] No hardcoded secrets
- [ ] Error handling implemented
- [ ] Input validation present
- [ ] Logging added for key operations
- [ ] No console.log in production code

---

# Quick Reference: PR Dependencies

```
PR #1 (Setup)
├─→ PR #2 (Backend) ──────→ PR #4 (Upload API) ──────→ PR #6 (AI)
│                                                         │
├─→ PR #3 (Frontend) ─────→ PR #5 (Upload UI)           │
                                                          │
                                                          ↓
                                                    PR #7 (Template)
                                                          │
                                                          ↓
                                                    PR #8 (Proof Gen)
                                                    │           │
                                                    ↓           ↓
                                            PR #9 (Preview) → PR #10 (Approval)
                                                                │
                                                                ↓
                                                          PR #11 (Download)
                                                                │
                                                                ↓
                                                          PR #12 (Errors)
                                                                │
                                                                ↓
                                                          PR #13 (Deploy)
                                                                │
                                                                ↓
                                                          PR #14 (Feedback DB)
                                                                │
                                                                ↓
                                                          PR #15 (Feedback API)
                                                                │
                                                                ↓
                                                          PR #16 (Feedback UI)
                                                                │
                                                                ↓
                                                          PR #17 (Campaign List)
                                                                │
                                                    ┌───────────┴───────────┐
                                                    ↓                       ↓
                                            PR #18 (Load Files)      PR #19 (Success Nav)
                                                    │                       │
                                                    └───────────┬───────────┘
                                                                ↓
                                                          PR #20 (Reject Confirm)
                                                                │
                                                    ┌───────────┴───────────┐
                                                    ↓                       ↓
                                            PR #21 (Edit/Regen)      PR #22 (History)
                                                    │                       │
                                                    └───────────┬───────────┘
                                                                ↓
                                                          PR #24 (Review)
                                                    │
                                                    ↓
                                            PR #23 (Scheduling)
```

---

# Time Tracking Template

Use this to track actual time vs. estimates:

| PR | Estimated | Actual | Delta | Notes |
|----|-----------|--------|-------|-------|
| #1 | 2h | | | ✅ Completed |
| #2 | 3h | | | ✅ Completed |
| #3 | 3h | | | ✅ Completed |
| #4 | 3h | | | ✅ Completed |
| #5 | 3h | | | ✅ Completed |
| #6 | 4h | | | ✅ Completed |
| #7 | 3h | | | ✅ Completed |
| #8 | 3h | | | ✅ Completed |
| #9 | 4h | | | ✅ Completed |
| #10| 3h | | | ✅ Completed |
| #11| 1h | | | ✅ Completed |
| #12| 3h | | | ✅ Completed |
| #13| 5h | | | ✅ Completed |
| #14| 1h | | | ✅ Completed |
| #15| 1h | | | ✅ Completed |
| #16| 2h | | | ✅ Completed |
| #17| 3h | | | ✅ Completed |
| #18| 2h | | | ✅ Completed |
| #19| 0.5h | | | ✅ Completed |
| #20| 1h | | | ✅ Completed |
| #21| 4h | | | ⏳ Proposed |
| #22| 2h | | | ⏳ Proposed |
| #23| 5h | | | ⏳ Proposed |
| #24| 4h | | | ⏳ Proposed |
| **Total** | **62.5h** | | | |

---

# PHASE 5: POST-MVP ENHANCEMENTS (Post-36h)

## PR #14: Backend - Add Feedback Field to Database & Models
**Branch:** `feature/feedback-database`  
**Time Estimate:** 1 hour  
**Dependencies:** PR #13  
**Status:** ✅ Completed

### Tasks
- [x] **14.1** Add feedback column to database schema
  - Update campaigns table creation
  - Add migration function for existing databases
  - Ensure column is nullable (TEXT)

- [x] **14.2** Update Campaign model
  - Add feedback field to __init__
  - Update from_row() to read feedback
  - Update to_dict() to include feedback
  - Update save() to persist feedback

- [x] **14.3** Update Pydantic schemas
  - Add optional feedback field to ApprovalRequest (max 2000 chars)
  - Add feedback field to ApprovalResponse
  - Add feedback field to CampaignResponse

**Acceptance Criteria:**
- ✅ Database migration adds feedback column
- ✅ Campaign model handles feedback field
- ✅ Schemas validate feedback input/output
- ✅ Existing campaigns work with null feedback

**Files Modified:**
- backend/app/database.py
- backend/app/models/campaign.py
- backend/app/models/schemas.py

---

## PR #15: Backend - Update Approval Route to Store Feedback
**Branch:** `feature/approval-feedback`  
**Time Estimate:** 1 hour  
**Dependencies:** PR #14  
**Status:** ✅ Completed

### Tasks
- [x] **15.1** Update approval endpoint
  - Accept feedback in ApprovalRequest
  - Store feedback for approve decisions
  - Store feedback for reject decisions
  - Update campaign record with feedback

- [x] **15.2** Include feedback in responses
  - Return feedback in ApprovalResponse
  - Log feedback (truncated for privacy)
  - Update proof service to include feedback in metadata

**Acceptance Criteria:**
- ✅ Approval endpoint accepts feedback parameter
- ✅ Feedback stored in database for both approve/reject
- ✅ Feedback returned in API response
- ✅ Feedback included in preview metadata

**Files Modified:**
- backend/app/routes/approve.py
- backend/app/services/proof_service.py

---

## PR #16: Frontend - Add Feedback UI & Display
**Branch:** `feature/feedback-ui`  
**Time Estimate:** 2 hours  
**Dependencies:** PR #15  
**Status:** ✅ Completed

### Tasks
- [x] **16.1** Update API service
  - Add feedback parameter to approveCampaign()
  - Send feedback in request body

- [x] **16.2** Update ApprovalButtons component
  - Add collapsible feedback textarea
  - Add character counter (2000 max)
  - Show feedback in confirmation dialog
  - Make feedback optional

- [x] **16.3** Update CampaignDetails component
  - Display feedback when available
  - Style feedback section appropriately
  - Preserve line breaks in feedback

**Acceptance Criteria:**
- ✅ Users can add feedback when approving/rejecting
- ✅ Feedback is optional (can be empty)
- ✅ Character limit enforced (2000 chars)
- ✅ Feedback displays in campaign details
- ✅ Feedback persists in database

**Files Modified:**
- frontend/src/services/api.js
- frontend/src/components/ApprovalButtons.jsx
- frontend/src/components/CampaignDetails.jsx

---

## PR #17: Backend & Frontend - Campaign List & Management
**Branch:** `feature/campaign-list`  
**Time Estimate:** 3 hours  
**Dependencies:** PR #16  
**Status:** ✅ Completed

### Tasks
- [x] **17.1** Backend: List campaigns endpoint
  - GET /api/v1/campaigns
  - Support pagination (limit, offset)
  - Support status filtering
  - Return list of CampaignResponse objects

- [x] **17.2** Backend: Campaign detail endpoint
  - GET /api/v1/campaigns/{campaign_id}
  - Return full campaign details including feedback
  - Use existing get_campaign service

- [x] **17.3** Backend: Reset rejected campaign endpoint
  - POST /api/v1/campaigns/{campaign_id}/reset
  - Reset rejected campaigns to 'uploaded' status
  - Clear feedback (optional)
  - Allow resubmission

- [x] **17.4** Frontend: Campaigns list page
  - Create CampaignsListPage component
  - Display table of all campaigns
  - Show status, created date, feedback preview
  - Add status filter dropdown
  - Add navigation to view/edit campaigns

- [x] **17.5** Frontend: API service methods
  - Add listCampaigns() method
  - Add getCampaignDetail() method
  - Add resetCampaign() method (optional)

- [x] **17.6** Frontend: Navigation updates
  - Add route for /campaigns
  - Add "View All Campaigns" link in header
  - Update routing in App.jsx

- [x] **17.7** Frontend: Edit rejected campaigns
  - Pre-fill upload form with existing campaign data
  - Allow modification and resubmission
  - Handle reset status flow

**Acceptance Criteria:**
- ✅ List campaigns endpoint returns all campaigns
- ✅ Status filtering works correctly
- ✅ Campaign detail endpoint returns full data
- ✅ Campaigns list page displays all campaigns
- ✅ Users can view feedback on campaigns
- ✅ Rejected campaigns can be reset and edited
- ✅ Navigation between pages works smoothly

**Files Created:**
- frontend/src/pages/CampaignsListPage.jsx

**Files Modified:**
- backend/app/routes/campaign.py
- frontend/src/services/api.js
- frontend/src/App.jsx
- frontend/src/components/Header.jsx (if exists)
- frontend/src/pages/UploadPage.jsx (for editing)

---

## PR #18: Frontend - Load and Display Existing Campaign Files When Editing
**Branch:** `feature/load-existing-files`  
**Time Estimate:** 2 hours  
**Dependencies:** PR #17  
**Status:** ✅ Completed

### Tasks
- [x] **18.1** Backend: Include file metadata in campaign detail response
  - Add `ai_processing_data` field to CampaignResponse schema (optional)
  - Update campaign detail endpoint to include `ai_processing_data`
  - Include logo and hero_images metadata with S3 URLs
  - Convert S3 URLs to presigned URLs for frontend access

- [x] **18.2** Frontend: Fetch and display existing files
  - When editing a campaign, fetch file URLs from campaign data
  - Download files from presigned URLs and convert to File objects
  - Display existing files in FileUpload components as if they were just uploaded
  - Show file previews for existing files

- [x] **18.3** Frontend: Pre-fill all form fields
  - Load content fields from `ai_processing_data.content`
  - Pre-fill subject_line, preview_text, body_copy, cta_text, cta_url, footer_text
  - Remove the "existing files" notice since files are now displayed

- [x] **18.4** Frontend: Handle file replacement
  - Allow users to replace existing files by uploading new ones
  - If no new files uploaded, keep existing files (loaded as File objects)
  - Update form validation to work with loaded existing files

- [x] **18.5** Backend: Update existing campaigns instead of creating new ones
  - Add optional `campaign_id` parameter to upload route
  - When `campaign_id` is provided and campaign is rejected, update existing campaign
  - Reset status to 'uploaded' and clear old proof/HTML paths when resubmitting
  - Pass `campaign_id` from frontend when editing

- [x] **18.6** Backend: Save campaign metadata changes when updating
  - Update `update_campaign_assets()` to accept and save `campaign_name` and `advertiser_name`
  - Ensure all modified campaign data is persisted when resubmitting

**Acceptance Criteria:**
- ✅ Campaign detail endpoint includes file metadata
- ✅ Existing files are displayed in upload form when editing
- ✅ All form fields (including content) are pre-filled from campaign data
- ✅ Users can see existing files and optionally replace them
- ✅ Form works seamlessly whether creating new or editing existing campaign
- ✅ Editing a rejected campaign updates the existing campaign (doesn't create duplicate)
- ✅ Campaign metadata changes (name, advertiser) are saved when resubmitting
- ✅ Status updates correctly after approval (shows 'approved' not 'rejected')

**Files Created:**
- frontend/src/utils/fileHelpers.js

**Files Modified:**
- backend/app/models/schemas.py
- backend/app/routes/campaign.py
- backend/app/routes/upload.py
- backend/app/services/campaign_service.py
- frontend/src/pages/UploadPage.jsx

---

## PR #19: Frontend - Add "View All Campaigns" Button to Success Page
**Branch:** `feature/success-page-navigation`  
**Time Estimate:** 30 minutes  
**Dependencies:** PR #17  
**Status:** ✅ Completed

### Tasks
- [x] **19.1** Frontend: Add "View All Campaigns" button
  - Add button to SuccessPage component
  - Place alongside "View Preview Again" and "Create New Campaign"
  - Navigate to `/campaigns` route

**Acceptance Criteria:**
- ✅ Success page displays "View All Campaigns" button
- ✅ Button navigates to campaigns list page
- ✅ Button is styled consistently with other navigation buttons

**Files Modified:**
- frontend/src/pages/SuccessPage.jsx

---

## PR #20: Frontend - Add Rejection Confirmation Dialog & Update Navigation
**Branch:** `feature/rejection-confirmation`  
**Time Estimate:** 1 hour  
**Dependencies:** PR #17  
**Status:** ✅ Completed

### Tasks
- [x] **20.1** Frontend: Add confirmation dialog for rejection
  - Add `showRejectConfirm` state to ApprovalButtons component
  - Show confirmation dialog before rejecting (similar to approval flow)
  - Display feedback in confirmation if provided
  - Require user confirmation before proceeding with rejection

- [x] **20.2** Frontend: Update rejection navigation
  - Change navigation destination from `/` to `/campaigns` after rejection
  - Remove state message about editing (no longer needed)
  - Navigate to campaigns list page after successful rejection

**Acceptance Criteria:**
- ✅ Rejection requires confirmation dialog (like approval)
- ✅ Confirmation shows feedback if provided
- ✅ After rejection, user is navigated to campaigns list page
- ✅ User can see rejected campaign in the list with feedback

**Files Modified:**
- frontend/src/components/ApprovalButtons.jsx

---

# PHASE 6: P1 FEATURES (Should-Have)

## PR #21: Edit & Regenerate Feature
**Branch:** `feature/edit-regenerate`  
**Time Estimate:** 4 hours  
**Dependencies:** PR #9, PR #8  
**Status:** ⏳ Proposed

### Tasks
- [ ] **21.1** Backend: Add edit endpoint
  - POST /api/v1/campaigns/{campaign_id}/edit
  - Accept partial updates (text fields only)
  - Validate edited content
  - Update campaign data without re-processing images

- [ ] **21.2** Backend: Add image replacement endpoint
  - POST /api/v1/campaigns/{campaign_id}/replace-image
  - Accept image type (logo or hero_image_index)
  - Upload new image to S3
  - Update campaign metadata
  - Keep other images unchanged

- [ ] **21.3** Backend: Regenerate proof endpoint
  - POST /api/v1/campaigns/{campaign_id}/regenerate
  - Use updated campaign data
  - Regenerate HTML proof with new content/images
  - Update preview in <2 seconds

- [ ] **21.4** Frontend: Inline text editing UI
  - Make text fields editable in preview page
  - Add "Edit" mode toggle
  - Show save/cancel buttons
  - Real-time validation

- [ ] **21.5** Frontend: Image replacement UI
  - Add "Replace Image" button on each image
  - File upload dialog for replacement
  - Show loading state during replacement
  - Update preview immediately after replacement

- [ ] **21.6** Frontend: Instant regeneration
  - "Regenerate Preview" button
  - Show loading spinner (<2 sec)
  - Update preview without page reload
  - Success/error notifications

**Acceptance Criteria:**
- ✅ Users can edit text fields inline in preview
- ✅ Users can replace individual images without full re-upload
- ✅ Preview regenerates in <2 seconds
- ✅ Changes persist in database
- ✅ No need to re-upload all assets

**Files Created:**
- backend/app/routes/edit.py

**Files Modified:**
- backend/app/routes/generate.py (add regenerate endpoint)
- backend/app/services/campaign_service.py
- frontend/src/pages/PreviewPage.jsx
- frontend/src/components/CampaignDetails.jsx
- frontend/src/services/api.js

---

## PR #22: Campaign History Enhancement
**Branch:** `feature/campaign-history`  
**Time Estimate:** 2 hours  
**Dependencies:** PR #17  
**Status:** ⏳ Proposed

### Tasks
- [ ] **22.1** Backend: Enhance campaigns list endpoint
  - Add "last 10" filter option
  - Add sorting by created_at (newest first)
  - Include quick stats (total campaigns, by status)

- [ ] **22.2** Frontend: Campaign history view
  - Show last 10 campaigns by default
  - Display campaign name, timestamp, status prominently
  - Add "View All" link to see full list
  - Compact card layout for history view

- [ ] **22.3** Frontend: Quick actions in history
  - "Re-download HTML" button for approved campaigns
  - "View Preview" button for all campaigns
  - "Edit" button for rejected campaigns
  - Status badges (approved/rejected/ready)

- [ ] **22.4** Frontend: History page route
  - Add /history route
  - Link from header navigation
  - Show as default view or separate page

**Acceptance Criteria:**
- ✅ History shows last 10 campaigns
- ✅ Metadata displays correctly (name, timestamp, status)
- ✅ Quick actions work (re-download, view preview)
- ✅ History page is easily accessible
- ✅ Integrates with existing campaign list

**Files Modified:**
- backend/app/routes/campaign.py
- frontend/src/pages/CampaignsListPage.jsx (or create HistoryPage.jsx)
- frontend/src/App.jsx
- frontend/src/components/Header.jsx
- frontend/src/services/api.js

---

## PR #23: Campaign Scheduling System
**Branch:** `feature/campaign-scheduling`  
**Time Estimate:** 5 hours  
**Dependencies:** PR #17  
**Status:** ⏳ Proposed

### Tasks
- [ ] **23.1** Backend: Add scheduling fields to database
  - Add `scheduled_at` datetime field to campaigns table
  - Add `scheduling_status` field (pending/scheduled/sent)
  - Migration script for existing campaigns

- [ ] **23.2** Backend: Scheduling endpoint
  - POST /api/v1/campaigns/{campaign_id}/schedule
  - Accept scheduled_at datetime
  - Validate future dates only
  - Update campaign scheduling status

- [ ] **23.3** Backend: Scheduled job processor (basic)
  - Background task to check scheduled campaigns
  - Mark campaigns as "sent" when scheduled time arrives
  - Log scheduling events
  - Note: Actual email sending out of scope (just status update)

- [ ] **23.4** Frontend: Scheduling UI
  - Add "Schedule Campaign" button on approved campaigns
  - Date/time picker component
  - Show scheduled campaigns in list with badge
  - Display scheduled date/time

- [ ] **23.5** Frontend: Scheduled campaigns view
  - Filter for scheduled campaigns
  - Show countdown to scheduled time
  - Allow canceling scheduled campaigns

**Acceptance Criteria:**
- ✅ Users can schedule approved campaigns
- ✅ Scheduled date/time is validated (future only)
- ✅ Scheduled campaigns show in list with status
- ✅ Background processor updates status at scheduled time
- ✅ Users can cancel scheduled campaigns

**Files Created:**
- backend/app/services/scheduler_service.py
- backend/app/routes/schedule.py

**Files Modified:**
- backend/app/database.py
- backend/app/models/campaign.py
- backend/app/models/schemas.py
- frontend/src/pages/CampaignsListPage.jsx
- frontend/src/services/api.js

---

## PR #24: Editorial Review Interface
**Branch:** `feature/editorial-review`  
**Time Estimate:** 4 hours  
**Dependencies:** PR #9, PR #21  
**Status:** ⏳ Proposed

### Tasks
- [ ] **24.1** Backend: Review status tracking
  - Add `review_status` field (pending/reviewed/approved/rejected)
  - Add `reviewer_notes` field (optional text)
  - Update approval workflow to include review step

- [ ] **24.2** Backend: Review endpoints
  - POST /api/v1/campaigns/{campaign_id}/review
  - Accept review decision and notes
  - Update review status
  - Separate from advertiser approval

- [ ] **24.3** Frontend: Review interface
  - Dedicated review page for campaign managers
  - Side-by-side content review
  - Highlight editable sections
  - Add reviewer notes section

- [ ] **24.4** Frontend: Review workflow UI
  - "Mark as Reviewed" button
  - Notes textarea for reviewer comments
  - Status indicators (pending review, reviewed, etc.)
  - Filter campaigns by review status

- [ ] **24.5** Frontend: Content editing in review
  - Allow editing content during review
  - Save review edits
  - Show diff/changes made during review

**Acceptance Criteria:**
- ✅ Review interface is user-friendly
- ✅ Reviewers can add notes and make edits
- ✅ Review status is tracked separately from approval
- ✅ Campaigns can be filtered by review status
- ✅ Review workflow integrates with existing approval flow

**Files Created:**
- frontend/src/pages/ReviewPage.jsx
- backend/app/routes/review.py

**Files Modified:**
- backend/app/database.py
- backend/app/models/campaign.py
- backend/app/models/schemas.py
- backend/app/routes/approve.py
- frontend/src/pages/CampaignsListPage.jsx
- frontend/src/services/api.js

---

**Document Status:** Ready for development  
**Last Updated:** November 2025  
**Version:** 1.3
