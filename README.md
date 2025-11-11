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
- Docker and Docker Compose
- AWS account with S3 bucket
- OpenAI API key

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EmailAds
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your credentials
   ```

3. **Start services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

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
- [Task Breakdown](TASK_BREAKDOWN.md) - Development roadmap (13 PRs)
- [Architecture Diagram](ARCHITECTURE.mermaid) - System architecture
- [Deployment Quickstart](DEPLOYMENT_QUICKSTART.md) - Quick deployment guide
- [AWS Deployment Guide](AWS_DEPLOYMENT_GUIDE.md) - Comprehensive deployment docs

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

## 📝 License

[Add your license here]

## 👥 Contributors

[Add contributors here]

---

**Status:** In Development  
**Version:** 1.0 MVP  
**Last Updated:** November 2025

