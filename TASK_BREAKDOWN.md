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
                        TOTAL: 13 PRs
```

---

# PHASE 1: FOUNDATION (Hours 0-8)

## PR #1: Project Setup & Infrastructure
**Branch:** `feature/project-setup`  
**Time Estimate:** 2 hours  
**Dependencies:** None

### Tasks
- [ ] **1.1** Initialize Git repository
  - Create .gitignore (Python, Node, env files)
  - Set up main branch
  - Create README.md with project overview

- [ ] **1.2** Set up project structure
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

- [ ] **1.3** Create Docker configuration
  - Backend Dockerfile (Python 3.11)
  - Frontend Dockerfile (Node 18)
  - docker-compose.yml for local development
  - Health check endpoints

- [ ] **1.4** Set up environment variables
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

### Tasks
- [ ] **2.1** Install backend dependencies
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

- [ ] **2.2** Create FastAPI application structure
  - main.py with CORS middleware
  - config.py with settings (Pydantic BaseSettings)
  - Health check endpoint
  - API versioning (/api/v1/)

- [ ] **2.3** Set up SQLite database
  - Create database schema (campaigns table)
  - Database connection manager
  - Async database operations with aiosqlite
  - Migration script (initial schema)

- [ ] **2.4** Create data models
  - Pydantic models for request/response
  - SQLAlchemy models for database
  - Campaign model with all fields
  - Asset metadata model

- [ ] **2.5** AWS S3 integration setup
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

### Tasks
- [ ] **3.1** Initialize React + Vite project
  ```bash
  npm create vite@latest frontend -- --template react
  cd frontend
  npm install
  ```

- [ ] **3.2** Install frontend dependencies
  ```
  axios
  react-router-dom
  react-dropzone
  tailwindcss
  postcss
  autoprefixer
  ```

- [ ] **3.3** Configure Tailwind CSS
  - tailwind.config.js
  - postcss.config.js
  - Import Tailwind in index.css

- [ ] **3.4** Set up routing
  - React Router configuration
  - Route structure:
    - / → Upload page
    - /preview/:campaignId → Preview page
    - /success/:campaignId → Success page

- [ ] **3.5** Create API service layer
  - Axios instance with base URL
  - API methods for all endpoints
  - Error handling wrapper
  - Request/response interceptors

- [ ] **3.6** Create basic layout components
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

### Tasks
- [ ] **4.1** Create upload endpoint
  - POST /api/v1/upload
  - Multipart form data handling
  - File validation (size, type)
  - Generate unique campaign ID

- [ ] **4.2** File processing utilities
  - Image validation (PNG, JPG, JPEG)
  - File size checking (max 5MB)
  - Mime type verification
  - Temporary storage handling

- [ ] **4.3** S3 upload implementation
  - Upload logo to S3
  - Upload hero images to S3
  - Generate S3 object keys (campaign_id/filename)
  - Store file URLs in database

- [ ] **4.4** Campaign creation logic
  - Create campaign record in database
  - Store metadata (name, advertiser, timestamps)
  - Store S3 paths for assets
  - Return campaign ID to client

- [ ] **4.5** Error handling
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

### Tasks
- [ ] **5.1** Create upload form component
  - Campaign name input
  - Advertiser name input
  - Subject line input
  - Preview text input
  - Body copy textarea

- [ ] **5.2** Implement file upload UI
  - Drag-and-drop zone using react-dropzone
  - Logo upload (single file)
  - Hero images upload (1-3 files)
  - File preview thumbnails
  - Remove file functionality

- [ ] **5.3** Form validation
  - Required field checking
  - File size validation
  - File type validation
  - Real-time error messages

- [ ] **5.4** Form submission
  - Build FormData object
  - Call upload API
  - Show upload progress
  - Handle success/error states

- [ ] **5.5** UX enhancements
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

### Tasks
- [ ] **6.1** OpenAI service setup
  - Initialize OpenAI client
  - API key configuration
  - Error handling for API calls
  - Rate limit management

- [ ] **6.2** Text content processing
  - GPT-4 prompt for content optimization
  - Subject line generation (3 variations)
  - Preview text optimization
  - Body copy structuring
  - JSON response parsing

- [ ] **6.3** Image analysis with GPT-4 Vision
  - Image-to-base64 conversion
  - Alt text generation for each image
  - Image quality assessment
  - Crop suggestions (if needed)

- [ ] **6.4** Image optimization
  - Resize images to email-safe dimensions
  - Logo: max 300x100px
  - Hero: max 600x400px
  - File compression (target <150KB)
  - Format conversion if needed

- [ ] **6.5** Process endpoint
  - POST /api/v1/process/{campaign_id}
  - Parallel processing of text and images
  - Aggregate results
  - Store AI outputs in database
  - Return processed data

- [ ] **6.6** Performance optimization
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

### Tasks
- [ ] **7.1** Create MJML template
  - Responsive email structure
  - Header with logo
  - Hero image section
  - Headline section
  - Body copy section
  - CTA button
  - Footer
  - Mobile optimization

- [ ] **7.2** Template variable system
  - Define template variables
  - Variable substitution logic
  - Jinja2 or string templating
  - Safe HTML escaping

- [ ] **7.3** HTML generation service
  - MJML to HTML conversion
  - CSS inlining (inline all styles)
  - Image URL injection
  - Production HTML output

- [ ] **7.4** Template population
  - Inject campaign content
  - Inject optimized AI content
  - Inject S3 image URLs
  - Generate alt texts

- [ ] **7.5** Email client testing
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

### Tasks
- [ ] **8.1** Generate endpoint
  - POST /api/v1/generate/{campaign_id}
  - Fetch campaign data from database
  - Fetch processed AI content
  - Call template service

- [ ] **8.2** Proof generation logic
  - Populate template with data
  - Generate HTML proof
  - Create desktop preview
  - Create mobile preview
  - Store proof in S3

- [ ] **8.3** Preview data structure
  - HTML content for rendering
  - Metadata (subject, preview text)
  - AI suggestions
  - Image URLs
  - Timestamp

- [ ] **8.4** Performance optimization
  - Cache generated proofs
  - Async HTML generation
  - Parallel S3 uploads
  - Total time <2 seconds

- [ ] **8.5** Update database
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

### Tasks
- [ ] **9.1** Preview page layout
  - Two-column layout (desktop + mobile)
  - Desktop preview (600px width)
  - Mobile preview (320px width)
  - Side-by-side comparison

- [ ] **9.2** HTML rendering
  - iframe for desktop preview
  - iframe for mobile preview
  - Sandboxed rendering
  - Responsive container

- [ ] **9.3** Campaign details panel
  - Show campaign name
  - Show subject line
  - Show preview text
  - Show AI suggestions
  - Editable fields (stretch goal)

- [ ] **9.4** Preview controls
  - Toggle desktop/mobile view
  - Fullscreen preview option
  - Refresh preview button
  - Download HTML button (coming in PR #10)

- [ ] **9.5** Loading states
  - Skeleton loader while generating
  - Preview loading spinner
  - Error state if generation fails

- [ ] **9.6** Fetch preview data
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

### Tasks
- [ ] **10.1** Approval endpoint
  - POST /api/v1/approve/{campaign_id}
  - Accept decision: 'approve' or 'reject'
  - Update campaign status
  - Generate final HTML if approved

- [ ] **10.2** Final HTML generation
  - Create production-ready HTML
  - Inline all CSS
  - Embed or link images (configurable)
  - Upload to S3 with unique name
  - Return download URL

- [ ] **10.3** Approval UI buttons
  - Approve button (green, prominent)
  - Reject button (red, secondary)
  - Confirmation modal for approval
  - Loading state during processing

- [ ] **10.4** Success page
  - Confirmation message
  - Download button for HTML
  - View preview again option
  - Start new campaign button

- [ ] **10.5** Rejection flow
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

### Tasks
- [ ] **11.1** Download endpoint
  - GET /api/v1/download/{campaign_id}
  - Fetch final HTML from S3
  - Set correct content headers
  - Force download (not preview)

- [ ] **11.2** HTML export options
  - Base64 encoded images (self-contained)
  - External image URLs (smaller file)
  - User choice in UI (optional)

- [ ] **11.3** Download UI
  - Download button on success page
  - File naming: {campaign_name}_{date}.html
  - Progress indicator
  - Success notification

- [ ] **11.4** Alternative: Copy to clipboard
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

### Tasks
- [ ] **12.1** Backend error handling
  - Global exception handler
  - Custom error classes
  - User-friendly error messages
  - Error logging

- [ ] **12.2** Input validation
  - Pydantic validators for all models
  - File type validation
  - File size validation
  - URL validation
  - Text length limits

- [ ] **12.3** Frontend error handling
  - API error interceptor
  - User-friendly error messages
  - Error boundary component
  - Retry logic for failed requests

- [ ] **12.4** Loading & feedback states
  - Loading spinners for all async operations
  - Progress indicators
  - Success notifications
  - Error notifications

- [ ] **12.5** Edge case handling
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

### Tasks
- [ ] **13.1** Backend testing
  - Unit tests for key functions
  - API endpoint tests (pytest)
  - S3 upload test
  - Database operations test
  - AI service mocks

- [ ] **13.2** Frontend testing
  - Component rendering tests (Vitest)
  - API service tests
  - Form validation tests
  - User flow tests

- [ ] **13.3** Integration testing
  - End-to-end upload flow
  - Preview generation
  - Approval workflow
  - Download functionality

- [ ] **13.4** Performance testing
  - Measure proof generation time
  - Test with large images
  - Test concurrent requests
  - Identify bottlenecks

- [ ] **13.5** Documentation
  - API documentation (OpenAPI/Swagger)
  - README.md with setup instructions
  - Environment variables documentation
  - Deployment guide
  - User guide

- [ ] **13.6** Deployment preparation
  - Production environment variables
  - Docker build optimization
  - Health check endpoints
  - Logging configuration
  - Monitoring setup (basic)

- [ ] **13.7** Final deployment
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
```

---

# Time Tracking Template

Use this to track actual time vs. estimates:

| PR | Estimated | Actual | Delta | Notes |
|----|-----------|--------|-------|-------|
| #1 | 2h | | | |
| #2 | 3h | | | |
| #3 | 3h | | | |
| #4 | 3h | | | |
| #5 | 3h | | | |
| #6 | 4h | | | |
| #7 | 3h | | | |
| #8 | 3h | | | |
| #9 | 4h | | | |
| #10| 3h | | | |
| #11| 1h | | | |
| #12| 3h | | | |
| #13| 5h | | | |
| **Total** | **36h** | | | |

---

**Document Status:** Ready for development  
**Last Updated:** November 11, 2025  
**Version:** 1.0
