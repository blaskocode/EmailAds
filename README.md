# HiBid Email MVP

Automated email advertising workflow system that reduces campaign setup from hours to minutes through AI-powered asset extraction and proof generation.

## 🎯 Project Overview

This MVP delivers an end-to-end automated email advertising workflow that:
- Processes campaign assets (logo, images, text) via AI
- Generates email proofs in under 5 seconds
- Provides real-time preview (desktop + mobile)
- Enables simple approval workflow
- Exports production-ready HTML

## 🏗️ Architecture

- **Frontend:** React 18 + Vite + Tailwind CSS
- **Backend:** FastAPI (Python 3.11+)
- **AI:** OpenAI GPT-4 + Vision API
- **Storage:** AWS S3
- **Database:** SQLite
- **Infrastructure:** Docker containers

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose (v2.0+)
- AWS account with S3 bucket configured
- OpenAI API key with GPT-4 access
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/blaskocode/EmailAds.git
   cd EmailAds
   ```

2. **Set up environment variables**
   
   Create `backend/.env` file:
   ```bash
   cp backend/.env.example backend/.env
   ```
   
   Edit `backend/.env` with your credentials:
   ```bash
   # OpenAI
   OPENAI_API_KEY=sk-your-openai-api-key
   
   # AWS
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your-bucket-name
   
   # Application
   DATABASE_URL=sqlite:///./data/campaigns.db
   FRONTEND_URL=http://localhost:3000
   BACKEND_URL=http://localhost:8000
   LOG_LEVEL=INFO
   ```

3. **Start services with Docker**
   ```bash
   docker-compose up --build
   ```
   
   Or start services separately:
   ```bash
   # Backend only
   cd backend
   docker build -t emailads-backend .
   docker run -p 8000:8000 --env-file .env emailads-backend
   
   # Frontend only
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Interactive API Docs: http://localhost:8000/docs
   - ReDoc API Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

### Manual Setup (Without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
EmailAds/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── utils/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 📚 Documentation

- [MVP PRD](MVP_PRD.md) - Complete product requirements
- [API Documentation](API_DOCS.md) - Comprehensive API reference
- [Task Breakdown](TASK_BREAKDOWN.md) - Development roadmap (13 PRs)
- [Architecture Diagram](ARCHITECTURE.mermaid) - System architecture
- [Deployment Quickstart](DEPLOYMENT_QUICKSTART.md) - Quick deployment guide
- [AWS Deployment Guide](AWS_DEPLOYMENT_GUIDE.md) - Comprehensive deployment docs

## 🧪 Testing

### Running Tests

**Backend Tests:**
```bash
cd backend
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest --cov=app          # With coverage
pytest tests/test_main.py # Run specific test file
```

**Frontend Tests:**
```bash
cd frontend
npm test                  # Run tests in watch mode
npm run test:ui          # Run with UI
npm run test:coverage    # Run with coverage report
```

### Test Coverage

- Target coverage: >60% for MVP
- Backend: Unit tests for services, routes, and utilities
- Frontend: Component tests and API service tests

## 🧪 Development Workflow

This project follows a 36-hour development plan with 13 PRs across 4 phases:

1. **Phase 1: Foundation** (0-8h) - Setup, backend, frontend
2. **Phase 2: Core Features** (8-20h) - Upload, AI, templates, proof generation
3. **Phase 3: UI & Approval** (20-28h) - Preview, approval, download
4. **Phase 4: Polish** (28-36h) - Error handling, testing, deployment

See [TASK_BREAKDOWN.md](TASK_BREAKDOWN.md) for detailed task lists.

## 🔑 Environment Variables

Required environment variables (see `backend/.env.example`):

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# AWS
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
S3_BUCKET_NAME=hibid-email-assets

# Application
DATABASE_URL=sqlite:///./data/campaigns.db
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

## 📊 Key Requirements

- **Proof generation:** <5 seconds (hard requirement)
- **End-to-end completion:** <10 minutes
- **AI extraction accuracy:** >80%
- **System availability:** >95%

## 🛠️ Tech Stack

### Backend
- FastAPI 0.104.1
- Python 3.11+
- SQLite (aiosqlite)
- boto3 (AWS S3)
- OpenAI API
- Pillow (image processing)

### Frontend
- React 18
- Vite
- Tailwind CSS
- Axios
- React Router
- react-dropzone

## 📖 Usage Guide

### Creating a Campaign

1. **Upload Assets**
   - Navigate to http://localhost:3000
   - Fill in campaign details (name, advertiser, subject, etc.)
   - Upload logo image (required)
   - Upload 1-3 hero images (optional)
   - Submit the form

2. **AI Processing**
   - System automatically processes your campaign
   - AI optimizes text content and generates variations
   - Images are analyzed and optimized
   - Processing completes in <5 seconds

3. **Preview & Approve**
   - Review the generated email proof
   - View desktop and mobile previews
   - Check AI suggestions for content
   - Approve or reject the campaign

4. **Download**
   - After approval, download the production-ready HTML
   - HTML is optimized for email clients
   - Ready to use in your email marketing platform

### API Usage Example

```bash
# 1. Upload campaign
curl -X POST "http://localhost:8000/api/v1/upload" \
  -F "campaign_name=Summer Sale" \
  -F "advertiser_name=Acme Corp" \
  -F "logo=@logo.png" \
  -F "subject_line=Summer Sale - 50% Off"

# Response: {"campaign_id": "uuid-here", "status": "uploaded"}

# 2. Process with AI
curl -X POST "http://localhost:8000/api/v1/process/{campaign_id}"

# 3. Generate proof
curl -X POST "http://localhost:8000/api/v1/generate/{campaign_id}"

# 4. Get preview
curl "http://localhost:8000/api/v1/preview/{campaign_id}"

# 5. Approve
curl -X POST "http://localhost:8000/api/v1/approve/{campaign_id}" \
  -H "Content-Type: application/json" \
  -d '{"decision": "approve"}'

# 6. Download HTML
curl -O -J "http://localhost:8000/api/v1/download/{campaign_id}"
```

See [API_DOCS.md](API_DOCS.md) for complete API documentation.

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check that all environment variables are set in `backend/.env`
- Verify AWS credentials and S3 bucket name
- Ensure OpenAI API key is valid
- Check database file permissions: `chmod 664 data/campaigns.db`

**Frontend won't connect to backend:**
- Verify `BACKEND_URL` in environment matches backend port
- Check CORS settings in `backend/app/main.py`
- Ensure backend is running on port 8000

**S3 upload fails:**
- Verify AWS credentials are correct
- Check S3 bucket exists and is accessible
- Ensure IAM user has `s3:PutObject` and `s3:GetObject` permissions

**AI processing fails:**
- Verify OpenAI API key is valid
- Check API key has GPT-4 access
- Review rate limits in OpenAI dashboard
- Check logs for detailed error messages

**Tests fail:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- For frontend: `npm install`
- Check test database permissions
- Verify environment variables for test setup

## 🚀 Deployment

See [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md) for quick deployment instructions or [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md) for comprehensive AWS deployment guide.

## 📝 License

[Add your license here]

## 👥 Contributors

[Add contributors here]

---

**Status:** MVP Complete  
**Version:** 1.0.0  
**Last Updated:** November 2025

