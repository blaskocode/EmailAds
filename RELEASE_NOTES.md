# Release Notes

## v1.5.0 - Production Deployment Release
**Release Date:** November 12, 2025  
**Status:** ✅ Production Ready

---

## 🎉 Major Milestone

This release marks the successful production deployment of the HiBid Email MVP to AWS EC2. All P1 features are complete and deployed, with full production configuration and infrastructure.

---

## 🚀 What's New in v1.5.0

### Production Deployment
- **AWS EC2 Infrastructure** - Successfully deployed to t3.medium instance
- **Elastic IP** - Application accessible at http://44.212.209.159:3000
- **S3 Bucket** - Configured: hibid-email-mvp-assets-1762970982
- **Production Build** - Frontend built with nginx for production
- **Environment Configuration** - Production .env file configured with all required variables

### Bug Fixes
- **Frontend Production Build** - Fixed Dockerfile to use multi-stage build with nginx
- **API URL Configuration** - Fixed frontend to use production backend URL instead of localhost
- **CORS Issues** - Resolved all CORS and network connectivity issues
- **S3 Lifecycle Policy** - Fixed JSON format (ID vs Id) in setup script

### Infrastructure Improvements
- **Docker Configuration** - Updated docker-compose.prod.yml for production
- **Port Mapping** - Corrected frontend port mapping (3000:80 for nginx)
- **Health Checks** - Backend health check endpoint verified
- **Container Management** - Both frontend and backend containers running successfully

---

## 📦 Complete Feature Set

### P0 Requirements (100% Complete)
- ✅ Asset Collection System
- ✅ Email Proof Generation (<5 seconds)
- ✅ Real-Time Preview System
- ✅ Advertiser Feedback/Approval Workflow

### P1 Requirements (100% Complete)
- ✅ Campaign Scheduling and Staging System (PR #23)
- ✅ Editorial Review Interface (PR #24)

### Additional Features
- ✅ Edit & Regenerate Feature (PR #21)
- ✅ Campaign History Enhancement (PR #22)
- ✅ Campaign Management & List View
- ✅ File Loading When Editing
- ✅ Feedback System

---

## 🔧 Technical Details

### Backend
- FastAPI application running on port 8000
- SQLite database (with migration path to PostgreSQL)
- S3 integration for asset storage
- OpenAI GPT-4 integration for AI processing
- Background scheduler service for campaign scheduling

### Frontend
- React 18 + Vite application
- Nginx production server on port 80 (mapped to 3000)
- Tailwind CSS for styling
- Responsive design (desktop + mobile)

### Infrastructure
- AWS EC2 (t3.medium)
- AWS S3 for asset storage
- Docker & Docker Compose for containerization
- Health check endpoints
- Production logging configuration

---

## 📊 Performance Metrics

- **Proof Generation:** <5 seconds ✅ (hard requirement met)
- **Preview Loading:** <1 second (cached)
- **API Response:** <500ms (95th percentile)
- **Upload:** <1 second

---

## 🐛 Known Issues

- Test coverage below 60% target (infrastructure ready, needs expansion)
- No authentication system (by design for MVP)
- SQLite database (single connection limit, migration path ready)

---

## 📝 Migration Notes

### For Existing Deployments
- Frontend Dockerfile has been updated - rebuild required
- Environment variables must include correct BACKEND_URL
- S3 lifecycle policy format corrected in setup script

### Database
- All migrations are backward compatible
- Existing campaigns will work with new features
- Performance tracking fields added (for future PR #25)

---

## 🔗 Links

- **Frontend:** http://44.212.209.159:3000
- **Backend API:** http://44.212.209.159:8000
- **API Docs:** http://44.212.209.159:8000/docs
- **Health Check:** http://44.212.209.159:8000/health

---

## 🙏 Acknowledgments

All P1 features completed and successfully deployed to production. The application is now ready for real-world usage and monitoring.

---

## 📚 Previous Releases

### v1.4.0 - P1 Features Complete
- PR #24: Editorial Review Interface
- All P1 requirements met

### v1.3.3 - Campaign Scheduling System
- PR #23: Campaign Scheduling and Staging System

### v1.3.2 - Campaign History Enhancement
- PR #22: Campaign History with quick actions

### v1.3.1 - Edit & Regenerate
- PR #21: Inline editing and instant regeneration

### v1.2.0 - Complete Feature Set
- All MVP and Post-MVP features
- Campaign management system
- Feedback system

### v1.0.0 - MVP Complete
- All 13 core PRs completed
- Core functionality working