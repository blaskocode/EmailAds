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
Phase 7: P2 Features            → 1 PR
Phase 8: UX IMPROVEMENTS        → 3 PRs
                        TOTAL: 28 PRs
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
                                                    │
                                                    ↓
                                            PR #25 (AI Recommendations)
                                                    │
                                                    ↓
                                            PR #26 (Default Route)
                                                    │
                                                    ↓
                                            PR #27 (UI Redesign)
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
| #21| 4h | | | ✅ Completed |
| #22| 2h | | | ✅ Completed |
| #23| 5h | | | ✅ Completed |
| #24| 4h | | | ✅ Completed |
| #25| 9h | | | ✅ Completed |
| #26| 1h | | | ✅ Completed |
| #27| 6h | | | ✅ Completed |
| **Total** | **78.5h** | | | |

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
**Status:** ✅ Completed

### Tasks
- [x] **21.1** Backend: Add edit endpoint
  - POST /api/v1/campaigns/{campaign_id}/edit
  - Accept partial updates (text fields only)
  - Validate edited content
  - Update campaign data without re-processing images

- [x] **21.2** Backend: Add image replacement endpoint
  - POST /api/v1/campaigns/{campaign_id}/replace-image
  - Accept image type (logo or hero_image_index)
  - Upload new image to S3
  - Update campaign metadata
  - Keep other images unchanged

- [x] **21.3** Backend: Regenerate proof endpoint
  - POST /api/v1/campaigns/{campaign_id}/regenerate
  - Use updated campaign data
  - Regenerate HTML proof with new content/images
  - Update preview in <2 seconds

- [x] **21.4** Frontend: Inline text editing UI
  - Make text fields editable in preview page
  - Add "Edit" mode toggle
  - Show save/cancel buttons
  - Real-time validation

- [x] **21.5** Frontend: Image replacement UI
  - Add "Replace Image" button on each image
  - File upload dialog for replacement
  - Show loading state during replacement
  - Update preview immediately after replacement

- [x] **21.6** Frontend: Instant regeneration
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
**Status:** ✅ Completed

### Tasks
- [x] **22.1** Backend: Enhance campaigns list endpoint
  - Add "last 10" filter option
  - Add sorting by created_at (newest first)
  - Include quick stats (total campaigns, by status)

- [x] **22.2** Frontend: Campaign history view
  - Show last 10 campaigns by default
  - Display campaign name, timestamp, status prominently
  - Add "View All" link to see full list
  - Compact card layout for history view

- [x] **22.3** Frontend: Quick actions in history
  - "Re-download HTML" button for approved campaigns
  - "View Preview" button for all campaigns
  - "Edit" button for rejected campaigns
  - Status badges (approved/rejected/ready)

- [x] **22.4** Frontend: History page route
  - Add /history route
  - Link from header navigation
  - Show as default view or separate page

**Acceptance Criteria:**
- ✅ History shows last 10 campaigns
- ✅ Metadata displays correctly (name, timestamp, status)
- ✅ Quick actions work (re-download, view preview)
- ✅ History page is easily accessible
- ✅ Integrates with existing campaign list

**Files Created:**
- frontend/src/pages/HistoryPage.jsx

**Files Modified:**
- backend/app/routes/campaign.py
- backend/app/models/schemas.py
- frontend/src/App.jsx
- frontend/src/components/Header.jsx
- frontend/src/services/api.js

---

## PR #23: Campaign Scheduling System
**Branch:** `feature/campaign-scheduling`  
**Time Estimate:** 5 hours  
**Dependencies:** PR #17  
**Status:** ✅ Completed

### Tasks
- [x] **23.1** Backend: Add scheduling fields to database
  - Add `scheduled_at` datetime field to campaigns table
  - Add `scheduling_status` field (pending/scheduled/sent)
  - Migration script for existing campaigns

- [x] **23.2** Backend: Scheduling endpoint
  - POST /api/v1/campaigns/{campaign_id}/schedule
  - Accept scheduled_at datetime
  - Validate future dates only
  - Update campaign scheduling status

- [x] **23.3** Backend: Scheduled job processor (basic)
  - Background task to check scheduled campaigns
  - Mark campaigns as "sent" when scheduled time arrives
  - Log scheduling events
  - Note: Actual email sending out of scope (just status update)

- [x] **23.4** Frontend: Scheduling UI
  - Add "Schedule Campaign" button on approved campaigns
  - Date/time picker component
  - Show scheduled campaigns in list with badge
  - Display scheduled date/time

- [x] **23.5** Frontend: Scheduled campaigns view
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
- backend/app/routes/campaign.py
- backend/app/main.py
- frontend/src/pages/CampaignsListPage.jsx
- frontend/src/services/api.js

---

## PR #24: Editorial Review Interface
**Branch:** `feature/editorial-review`  
**Time Estimate:** 4 hours  
**Dependencies:** PR #9, PR #21  
**Status:** ✅ Completed

### Tasks
- [x] **24.1** Backend: Review status tracking
  - Add `review_status` field (pending/reviewed/approved/rejected)
  - Add `reviewer_notes` field (optional text)
  - Update approval workflow to include review step

- [x] **24.2** Backend: Review endpoints
  - POST /api/v1/campaigns/{campaign_id}/review
  - Accept review decision and notes
  - Update review status
  - Separate from advertiser approval

- [x] **24.3** Frontend: Review interface
  - Dedicated review page for campaign managers
  - Side-by-side content review
  - Highlight editable sections
  - Add reviewer notes section

- [x] **24.4** Frontend: Review workflow UI
  - "Mark as Reviewed" button
  - Notes textarea for reviewer comments
  - Status indicators (pending review, reviewed, etc.)
  - Filter campaigns by review status

- [x] **24.5** Frontend: Content editing in review
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
- backend/app/routes/campaign.py
- backend/app/main.py
- frontend/src/pages/CampaignsListPage.jsx
- frontend/src/services/api.js
- frontend/src/App.jsx

---

# PHASE 7: P2 FEATURES (Nice-to-Have)

## PR #25: AI-Based Content Suggestions from Past Performance
**Branch:** `feature/ai-content-suggestions`  
**Time Estimate:** 9 hours (updated: added test data generator)  
**Dependencies:** PR #17, PR #24  
**Status:** ✅ Completed

### Overview
Implement AI-based content suggestions that learn from past campaign performance to provide personalized recommendations. This addresses the P2 requirement gap where current AI suggestions are generated fresh per campaign without leveraging historical data.

### Tasks
- [x] **25.1** Backend: Campaign performance tracking
  - Add performance metrics fields to campaigns table
    - `open_rate` (optional, decimal)
    - `click_rate` (optional, decimal)
    - `conversion_rate` (optional, decimal)
    - `performance_score` (optional, decimal, calculated)
    - `performance_timestamp` (optional, datetime)
  - Create migration script for new fields
  - Update Campaign model to include performance fields
  - Add performance update endpoint (POST /api/v1/campaigns/{campaign_id}/performance)
    - Accept performance metrics from external systems
    - Calculate performance score
    - Update campaign record

- [x] **25.2** Backend: Analytics aggregation service
  - Create analytics service to aggregate campaign performance
  - Calculate average performance by:
    - Subject line patterns
    - Preview text patterns
    - CTA text patterns
    - Image count/type
    - Advertiser category (if available)
  - Store aggregated analytics in database (new `campaign_analytics` table)
  - Update analytics periodically (daily batch job or on-demand)

- [x] **25.3** Backend: Recommendation engine
  - Create recommendation service
  - Analyze current campaign content
  - Match against historical high-performing campaigns
  - Generate personalized suggestions based on:
    - Similar subject line patterns that performed well
    - Successful preview text styles
    - Effective CTA text variations
    - Optimal image count/arrangement
  - Return ranked suggestions with confidence scores

- [x] **25.4** Backend: Enhanced AI service integration
  - Update AI service to accept historical context
  - Pass top-performing examples to GPT-4 prompts
  - Generate suggestions that align with proven patterns
  - Combine AI creativity with data-driven insights
  - Fallback to standard AI suggestions if no historical data available

- [x] **25.5** Backend: Recommendations endpoint
  - POST /api/v1/campaigns/{campaign_id}/recommendations
  - Accept current campaign content
  - Return personalized suggestions:
    - Subject line recommendations (top 3-5)
    - Preview text recommendations (top 3-5)
    - CTA text recommendations (top 3-5)
    - Content structure suggestions
    - Image optimization suggestions
  - Include confidence scores and reasoning

- [x] **25.6** Frontend: Performance metrics display
  - Add performance section to CampaignDetails component
  - Display performance metrics (if available)
  - Show performance score with visual indicator
  - Add "View Performance" button for approved campaigns
  - Performance dashboard (optional, can be separate page)

- [x] **25.7** Frontend: Recommendations UI
  - Add "Get Recommendations" button in PreviewPage
  - Create recommendations panel/modal
  - Display personalized suggestions with confidence scores
  - Show reasoning (e.g., "Based on 12 similar high-performing campaigns")
  - Allow applying suggestions with one click
  - Show comparison: current vs. recommended

- [x] **25.8** Frontend: Analytics integration (optional)
  - Add analytics input form (for manual entry or future API integration)
  - Allow campaign managers to update performance metrics
  - Display analytics trends over time
  - Show top-performing campaigns

- [x] **25.9** Backend: Batch analytics job (optional)
  - Create background job to update analytics daily
  - Aggregate performance data
  - Calculate trends and patterns
  - Store in analytics table for fast retrieval

- [x] **25.10** Backend: Test data generator for demo purposes
  - Create test data generator service
  - Generate realistic performance metrics for approved campaigns
  - Support different performance tiers (high, medium, low performers)
  - Create endpoint: POST /api/v1/test/generate-performance-data
  - Find approved campaigns without performance data
  - Generate varied, realistic metrics (open_rate, click_rate, conversion_rate)
  - Update campaigns with generated metrics and calculated performance scores
  - Return summary of generated data

**Acceptance Criteria:**
- ✅ Campaign performance metrics can be stored and retrieved
- ✅ Analytics service aggregates historical performance data
- ✅ Recommendation engine generates personalized suggestions
- ✅ Suggestions are based on past high-performing campaigns
- ✅ Frontend displays recommendations with confidence scores
- ✅ Users can apply recommendations with one click
- ✅ System gracefully handles cases with no historical data
- ✅ Performance metrics are displayed for campaigns
- ✅ Test data generator creates realistic demo data for approved campaigns

**Files Created:**
- backend/app/services/analytics_service.py
- backend/app/services/recommendation_service.py
- backend/app/services/test_data_generator.py
- backend/app/routes/analytics.py
- backend/app/routes/recommendations.py
- frontend/src/components/RecommendationsPanel.jsx
- frontend/src/components/PerformanceMetrics.jsx

**Files Modified:**
- backend/app/database.py (add performance fields, analytics table)
- backend/app/models/campaign.py (add performance fields)
- backend/app/models/schemas.py (add performance schemas)
- backend/app/services/ai_service.py (integrate historical context)
- backend/app/routes/performance.py (add test data generator endpoint)
- backend/app/main.py (register test routes if separate file)
- frontend/src/pages/PreviewPage.jsx (add recommendations UI)
- frontend/src/components/CampaignDetails.jsx (add performance display)
- frontend/src/services/api.js (add recommendations endpoints)

**Technical Notes:**
- Performance metrics can be manually entered or integrated via API
- Recommendation engine uses pattern matching and similarity scoring
- GPT-4 prompts enhanced with top-performing examples as context
- Analytics aggregation runs on-demand or via scheduled job
- System works even with minimal historical data (graceful degradation)
- Test data generator creates realistic demo metrics for testing and demonstrations
- Test data generator distributes campaigns across performance tiers for varied recommendations

---

**Document Status:** Ready for development  
**Last Updated:** November 12, 2025  
**Version:** 1.5.1

---

# BUG FIXES & IMPROVEMENTS (Post-P2)

## Bug Fix: Preview Access for Approved Campaigns
**Status:** ✅ Completed  
**Date:** November 12, 2025

### Issue
Approved campaigns couldn't view their previews - error: "Campaign must be processed before generating proof. Current status: approved"

### Fixes Applied
- ✅ Updated `proof_service.py` to allow 'approved' status in validation (line 61)
- ✅ Updated `preview.py` endpoint to handle 'approved' status with cached proof (line 42)
- ✅ Updated `campaign.py` status endpoint to return `can_preview: true` for approved campaigns (line 232)
- ✅ Updated schema comments in `schemas.py` to reflect approved status support

### Files Modified
- `backend/app/services/proof_service.py`
- `backend/app/routes/preview.py`
- `backend/app/routes/campaign.py`
- `backend/app/models/schemas.py`

---

## Bug Fix: Prevent Re-Approval/Rejection of Approved Campaigns
**Status:** ✅ Completed  
**Date:** November 12, 2025

### Issue
Approved campaigns could still be approved or rejected again, showing approval buttons when they shouldn't.

### Fixes Applied
- ✅ Added backend validation in `approve.py` to prevent re-approval/rejection (line 49-53)
- ✅ Added `campaignStatus` state tracking in PreviewPage
- ✅ Added conditional rendering to hide approval buttons when campaign is approved
- ✅ Added approved status message display with checkmark icon
- ✅ **Verified:** Approval buttons correctly disappear for approved campaigns

### Files Modified
- `backend/app/routes/approve.py`
- `frontend/src/pages/PreviewPage.jsx`

---

## Code Quality: File Length Limit Compliance
**Status:** ✅ Completed  
**Date:** November 12, 2025

### Issue
`CampaignsListPage.jsx` exceeded 500-line limit (547 lines)

### Fixes Applied
- ✅ Split file into smaller modules:
  - Created `frontend/src/utils/campaignsListUtils.js` (constants and utilities)
  - Created `frontend/src/components/ScheduleModal.jsx` (schedule modal component)
  - Reduced main file to 452 lines (under 500 limit)
- ✅ All files now comply with 500-line limit rule

### Files Created
- `frontend/src/utils/campaignsListUtils.js`
- `frontend/src/components/ScheduleModal.jsx`

### Files Modified
- `frontend/src/pages/CampaignsListPage.jsx`

---

---

# PHASE 8: UX IMPROVEMENTS

## PR #26: Change Default Route to Campaigns List
**Branch:** `feature/default-route-campaigns`  
**Time Estimate:** 1 hour  
**Dependencies:** PR #17  
**Status:** ✅ Completed

### Overview
Change the default route ("/") to render CampaignsListPage instead of UploadPage, making the campaigns list the landing page. Move campaign creation to a dedicated "/create" route.

### Tasks
- [x] **26.1** Update App.jsx routing
  - Change "/" route to render CampaignsListPage
  - Move UploadPage to "/create" route
  - Ensure all existing routes remain functional

- [x] **26.2** Update Header navigation
  - Update "New Campaign" link to point to "/create"
  - Update "View All Campaigns" link to point to "/"
  - Ensure navigation reflects new route structure

- [x] **26.3** Update any hardcoded route references
  - Check all components for "/" references that should point to "/create"
  - Update success page navigation if needed
  - Update any redirects or navigation calls

**Acceptance Criteria:**
- ✅ "/" route displays CampaignsListPage
- ✅ "/create" route displays UploadPage
- ✅ Header navigation links work correctly
- ✅ All existing functionality preserved
- ✅ No broken links or navigation issues

**Files Modified:**
- frontend/src/App.jsx
- frontend/src/components/Header.jsx
- frontend/src/pages/SuccessPage.jsx
- frontend/src/pages/CampaignsListPage.jsx
- frontend/src/pages/HistoryPage.jsx

---

## PR #27: Modern Professional UI Redesign with HiBid Branding
**Branch:** `feature/modern-ui-redesign`  
**Time Estimate:** 6 hours  
**Dependencies:** PR #26  
**Status:** ✅ Completed

### Overview
Complete UI redesign to create a modern, professional application optimized for marketing teams. Implement HiBid brand colors (vibrant blue, light gray/white, dark gray), dashboard-style overview, card-based layouts, and enhanced user experience with quick actions, search, filters, and bulk operations.

### Tasks
- [x] **27.1** Update Tailwind configuration with HiBid brand colors
  - Define primary blue color (matching HiBid logo)
  - Define light gray/white colors (matching logo)
  - Define dark gray for text
  - Add gradient utilities for subtle depth effects
  - Update color palette throughout application

- [x] **27.2** Redesign CampaignsListPage with dashboard overview
  - Add stats cards at top (total campaigns, by status, recent activity)
  - Implement search bar with real-time filtering
  - Add advanced filters (status, date range, advertiser)
  - Convert to card-based grid layout
  - Add quick actions on each campaign card
  - Add bulk operations (select multiple, bulk actions)
  - Improve visual hierarchy and spacing
  - Created StatsCards component (extracted for file length compliance)
  - Created CampaignsSearchBar component (extracted for file length compliance)

- [x] **27.3** Redesign Header component
  - Update with HiBid branding (logo integration if available)
  - Modern navigation design
  - Improved spacing and typography
  - Add quick action buttons (Create Campaign prominently)
  - Professional color scheme

- [x] **27.4** Redesign UploadPage (Create Campaign)
  - Streamlined form layout for fast campaign creation
  - Improved visual feedback
  - Better file upload UI
  - Clear step indicators or progress
  - Modern form styling

- [x] **27.5** Redesign PreviewPage
  - Enhanced preview controls
  - Better campaign details sidebar
  - Improved action buttons
  - Modern card-based layout for details

- [x] **27.6** Redesign all components for consistency
  - Update CampaignDetails component
  - Update ApprovalButtons component
  - Update FileUpload component
  - Update FormInput component
  - Update Loading component
  - Update Toast component
  - Consistent spacing, typography, and colors

- [x] **27.7** Enhance empty states and loading states
  - Professional empty state designs
  - Improved loading spinners and skeletons
  - Better error state displays
  - Consistent messaging

- [x] **27.8** Add animations and transitions
  - Smooth transitions between states
  - Hover effects on interactive elements
  - Loading animations
  - Subtle micro-interactions

- [x] **27.9** Improve typography and spacing
  - Professional font stack (system fonts optimized)
  - Consistent spacing scale
  - Better text hierarchy
  - Improved readability

- [x] **27.10** Mobile responsiveness
  - Ensure all new designs work on mobile
  - Responsive grid layouts
  - Mobile-friendly navigation
  - Touch-friendly interactions

**Acceptance Criteria:**
- ✅ HiBid brand colors applied throughout application
- ✅ Dashboard-style overview on campaigns list
- ✅ Card-based layout for campaigns
- ✅ Search and filters functional
- ✅ Bulk operations available
- ✅ Fast campaign creation flow
- ✅ All components redesigned consistently
- ✅ Professional, modern appearance
- ✅ Intuitive for marketing teams
- ✅ Mobile responsive
- ✅ Smooth animations and transitions

**Files Modified:**
- frontend/tailwind.config.js (add HiBid brand colors, gradients, shadows)
- frontend/src/index.css (update base styles with HiBid colors)
- frontend/src/pages/CampaignsListPage.jsx (complete redesign with dashboard, stats, search)
- frontend/src/pages/UploadPage.jsx (redesign with modern styling)
- frontend/src/pages/PreviewPage.jsx (redesign with enhanced controls)
- frontend/src/components/Header.jsx (redesign with modern navigation and HiBid branding)
- frontend/src/components/CampaignDetails.jsx (redesign with HiBid colors)
- frontend/src/components/ApprovalButtons.jsx (redesign with modern styling)
- frontend/src/components/FileUpload.jsx (redesign with HiBid colors)
- frontend/src/components/FormInput.jsx (redesign with HiBid colors)
- frontend/src/components/Loading.jsx (redesign with HiBid colors)
- frontend/src/components/Toast.jsx (redesign with HiBid colors)

**Files Created:**
- frontend/src/components/StatsCards.jsx (new component - extracted for file length compliance)
- frontend/src/components/CampaignsSearchBar.jsx (new component - extracted for file length compliance)

**Design References:**
- Mailchimp (email campaign management)
- HubSpot Marketing Hub (dashboard overview)
- Notion (clean, modern interface)
- Linear (fast, intuitive design)
- Stripe Dashboard (professional, data-dense)

**Technical Notes:**
- Use HiBid brand colors: vibrant blue (primary), light gray/white (secondary), dark gray (text)
- Implement subtle gradients for depth (matching logo aesthetic)
- Card-based layout for better visual scanning
- Dashboard stats for quick overview
- Search and filters for efficient campaign management
- Bulk operations for productivity
- Fast creation flow as top priority

---

## PR #28: AI Mode - Prompt-Based Campaign Auto-Population
**Branch:** `feature/ai-mode-prompt`  
**Time Estimate:** 4-5 hours  
**Dependencies:** PR #27 (UI redesign)  
**Status:** ⏳ Pending

### Feature Overview
Add an AI mode to the Create New Campaign form where users can enter a natural language prompt describing their campaign, and the form will automatically populate with campaign details extracted by an LLM.

### Model Recommendation
**Suggested Model: `gpt-4o-mini`**
- Faster response times (better UX)
- Lower cost per request
- Sufficient for structured data extraction
- Good for form auto-population tasks
- Alternative: `gpt-4o` if higher quality is needed

### Tasks

#### Backend Tasks

- [ ] **28.1** Create new AI service function for prompt-based campaign generation
  - Function: `generate_campaign_from_prompt(prompt: str) -> Dict`
  - Use `gpt-4o-mini` model
  - Prompt engineering to extract:
    - Campaign name
    - Advertiser name
    - Subject line
    - Preview text
    - Body copy (structured as headline + paragraphs)
    - CTA text
    - CTA URL (if mentioned or inferred)
    - Footer text (optional)
  - Return structured JSON matching form fields
  - Handle edge cases (missing info, ambiguous prompts)

- [ ] **28.2** Create new API endpoint `/api/v1/campaigns/generate-from-prompt`
  - Method: POST
  - Request body: `{ "prompt": "string" }`
  - Response: `{ "campaign_name": "...", "advertiser_name": "...", ... }`
  - Error handling for API failures, invalid responses
  - Add rate limiting if needed

- [ ] **28.3** Add route handler in `backend/app/routes/generate.py`
  - Import new AI service function
  - Validate input (non-empty prompt, max length)
  - Call AI service
  - Return structured response
  - Logging for debugging

#### Frontend Tasks

- [ ] **28.4** Add AI Mode toggle/button to UploadPage
  - Toggle between "Manual Mode" and "AI Mode"
  - Visual indicator (icon, badge)
  - Position: top of form, near title

- [ ] **28.5** Create AI Mode UI component
  - Large textarea for user prompt
  - Placeholder with examples
  - "Generate Campaign" button
  - Loading state during generation
  - Error display for failures
  - Success feedback

- [ ] **28.6** Integrate AI generation with form
  - Call new API endpoint on "Generate Campaign"
  - Auto-populate all form fields from response
  - Preserve user's uploaded files (logo, hero images)
  - Allow editing after auto-population
  - Clear form option

- [ ] **28.7** Add API service function
  - Add `generateCampaignFromPrompt(prompt)` to `frontend/src/services/api.js`
  - Handle errors appropriately
  - Return structured data

- [ ] **28.8** Enhance UX
  - Show example prompts as suggestions
  - Allow switching between AI and Manual modes
  - Preserve form data when toggling
  - Visual feedback during generation
  - Toast notifications for success/errors

### Technical Specifications

**AI Prompt Template:**
```
You are an email marketing expert. Extract campaign information from the following user prompt:

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
6. Generate CTA text (2-4 words, action-oriented)
7. Extract or suggest CTA URL (if mentioned, or use placeholder)
8. Generate footer text (optional, company info or disclaimer)

OUTPUT FORMAT: JSON only, no markdown, no code blocks
{
  "campaign_name": "...",
  "advertiser_name": "...",
  "subject_line": "...",
  "preview_text": "...",
  "body_copy": "...",
  "cta_text": "...",
  "cta_url": "...",
  "footer_text": "..."
}
```

**API Parameters:**
- Model: `gpt-4o-mini`
- Temperature: 0.7 (creative but consistent)
- Max tokens: 1000
- Response format: JSON object

### Acceptance Criteria
- ✅ AI Mode toggle visible and functional
- ✅ Users can enter natural language prompts
- ✅ Form auto-populates with extracted data
- ✅ All form fields populated (with reasonable defaults if missing)
- ✅ Users can edit auto-populated fields
- ✅ Error handling for API failures
- ✅ Loading states during generation
- ✅ Works with existing file upload functionality
- ✅ Manual mode still works as before
- ✅ Smooth UX transitions between modes

### Example User Prompts
- "Create a campaign for Acme Corp's Black Friday sale. 30% off all products. Use code BLACKFRIDAY30."
- "I need an email campaign for TechStart's new product launch. The product is called CloudSync, a cloud storage solution for businesses."
- "Promote our summer collection sale. 50% off swimwear. Free shipping over $50."

### Files to Create
- `backend/app/services/prompt_service.py` (or add to `ai_service.py` if under 500 lines)
- `backend/app/routes/generate.py` (if not exists, or add to existing generate.py)

### Files to Modify
- `frontend/src/pages/UploadPage.jsx` (add AI mode UI and logic)
- `frontend/src/services/api.js` (add generateCampaignFromPrompt function)
- `backend/app/services/ai_service.py` (add prompt generation function)
- `backend/app/routes/generate.py` (add new endpoint)

### Design Considerations
- AI Mode should feel optional, not required
- Clear visual distinction between AI and Manual modes
- Example prompts help users understand capabilities
- Auto-populated fields should be clearly editable
- Preserve user work when switching modes

### Testing Checklist
- [ ] Test with various prompt styles (detailed, vague, partial info)
- [ ] Test error handling (API failures, network issues)
- [ ] Test form validation with AI-generated data
- [ ] Test mode switching (AI → Manual, Manual → AI)
- [ ] Test with file uploads (logo, hero images)
- [ ] Test edge cases (empty prompts, very long prompts, special characters)

**Note:** This feature enhances the campaign creation workflow by allowing users to describe their campaign in natural language, reducing manual data entry while maintaining full control to edit the generated content.
