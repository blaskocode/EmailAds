# Technical Context: HiBid Email MVP

---

## Technology Stack

### Backend
- **Framework:** FastAPI 0.104.1
- **Language:** Python 3.11+
- **ASGI Server:** Uvicorn 0.24.0
- **Database:** SQLite (aiosqlite 0.19.0)
- **ORM:** Custom async SQLite wrapper
- **Validation:** Pydantic 2.5.0
- **HTTP Client:** httpx 0.25.2 (for testing)

### Frontend
- **Framework:** React 18.2.0
- **Build Tool:** Vite 5.0.8
- **Styling:** Tailwind CSS 3.3.6
- **Routing:** React Router 6.20.0
- **HTTP Client:** Axios 1.6.2
- **File Upload:** react-dropzone 14.2.3
- **Testing:** Vitest 1.0.4, React Testing Library

### External Services
- **AI:** OpenAI API (GPT-4, GPT-4 Vision)
- **Storage:** AWS S3 (boto3 1.29.7)
- **Image Processing:** Pillow 10.1.0
- **Email Templates:** MJML (via mjml npm package)
- **CSS Inlining:** Premailer 3.10.0

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Deployment:** AWS EC2/ECS ready
- **Monitoring:** CloudWatch integration ready

---

## Development Environment

### Local Setup
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Docker
docker-compose up --build
```

### Environment Variables

**Required:**
- `OPENAI_API_KEY` - OpenAI API key
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `S3_BUCKET_NAME` - S3 bucket name
- `AWS_REGION` - AWS region (default: us-east-1)

**Optional:**
- `DATABASE_URL` - Database path (default: sqlite:///./data/campaigns.db)
- `FRONTEND_URL` - Frontend URL (default: http://localhost:3000)
- `BACKEND_URL` - Backend URL (default: http://localhost:8000)
- `LOG_LEVEL` - Logging level (default: INFO)
- `ALLOWED_ORIGINS` - CORS origins (comma-separated)

---

## Dependencies

### Backend Dependencies
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pillow==10.1.0
boto3==1.29.7
openai==1.3.7
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
aiosqlite==0.19.0
jinja2==3.1.2
premailer==3.10.0
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
pytest-mock==3.12.0
```

### Frontend Dependencies
```
react: ^18.2.0
react-dom: ^18.2.0
react-router-dom: ^6.20.0
axios: ^1.6.2
react-dropzone: ^14.2.3
```

### Frontend Dev Dependencies
```
@vitejs/plugin-react: ^4.2.1
tailwindcss: ^3.3.6
vite: ^5.0.8
vitest: ^1.0.4
@testing-library/react: ^14.1.2
@testing-library/jest-dom: ^6.1.5
jsdom: ^23.0.1
```

---

## Database Schema

### Campaigns Table
```sql
CREATE TABLE campaigns (
    id TEXT PRIMARY KEY,
    campaign_name TEXT NOT NULL,
    advertiser_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL,
    approved_at TEXT,
    assets_s3_path TEXT,
    html_s3_path TEXT,
    proof_s3_path TEXT,
    ai_processing_data TEXT,  -- JSON stored as text
    updated_at TEXT
)
```

**Status Values:**
- `draft` - Initial state
- `uploaded` - Assets uploaded
- `processed` - AI processing complete
- `ready` - Proof generated
- `approved` - Campaign approved
- `rejected` - Campaign rejected

---

## API Endpoints

### Base URL
`http://localhost:8000/api/v1`

### Endpoints
1. `POST /upload` - Upload campaign assets
2. `POST /process/{campaign_id}` - Process with AI
3. `POST /generate/{campaign_id}` - Generate proof
4. `GET /preview/{campaign_id}` - Get preview data
5. `POST /approve/{campaign_id}` - Approve/reject campaign
6. `GET /download/{campaign_id}` - Download HTML

### Health Check
`GET /health` - Service health status

---

## File Structure

### Backend
```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── models/              # Data models
│   │   ├── campaign.py      # Campaign model
│   │   └── schemas.py       # Pydantic schemas
│   ├── routes/              # API routes
│   │   ├── upload.py
│   │   ├── process.py
│   │   ├── generate.py
│   │   ├── preview.py
│   │   ├── approve.py
│   │   └── download.py
│   ├── services/            # Business logic
│   │   ├── ai_service.py
│   │   ├── campaign_service.py
│   │   ├── file_service.py
│   │   ├── image_service.py
│   │   ├── proof_service.py
│   │   ├── s3_service.py
│   │   └── template_service.py
│   ├── utils/                # Utilities
│   │   ├── error_handlers.py
│   │   ├── image_utils.py
│   │   ├── mjml_compiler.py
│   │   └── validators.py
│   └── templates/
│       └── email_template.mjml
├── tests/                   # Test suite
├── Dockerfile
├── requirements.txt
└── pytest.ini
```

### Frontend
```
frontend/
├── src/
│   ├── App.jsx              # Router setup
│   ├── main.jsx             # Entry point
│   ├── pages/                # Route pages
│   │   ├── UploadPage.jsx
│   │   ├── PreviewPage.jsx
│   │   └── SuccessPage.jsx
│   ├── components/           # Reusable components
│   │   ├── ApprovalButtons.jsx
│   │   ├── CampaignDetails.jsx
│   │   ├── ErrorBoundary.jsx
│   │   ├── FileUpload.jsx
│   │   ├── Footer.jsx
│   │   ├── FormInput.jsx
│   │   ├── Header.jsx
│   │   ├── Layout.jsx
│   │   ├── Loading.jsx
│   │   ├── PreviewFrame.jsx
│   │   └── Toast.jsx
│   ├── contexts/             # React contexts
│   │   └── ToastContext.jsx
│   ├── services/             # API client
│   │   └── api.js
│   ├── utils/                # Helpers
│   │   └── downloadHelpers.js
│   └── tests/                # Tests
├── Dockerfile
├── package.json
├── vite.config.js
└── tailwind.config.js
```

---

## Build & Deployment

### Docker Configuration
- **Backend:** Python 3.11 base image
- **Frontend:** Node 18 base image
- **Multi-stage builds** for optimization
- **Health checks** configured

### Deployment Options
1. **Docker Compose** - Local development
2. **AWS EC2** - Single instance deployment
3. **AWS ECS** - Container orchestration
4. **Manual** - Direct server deployment

### Build Commands
```bash
# Backend
docker build -t emailads-backend ./backend

# Frontend
docker build -t emailads-frontend ./frontend

# Both
docker-compose build
```

---

## Testing Infrastructure

### Backend Testing
- **Framework:** pytest 7.4.3
- **Async Support:** pytest-asyncio
- **Coverage:** pytest-cov
- **Mocks:** pytest-mock
- **Test Client:** httpx

### Frontend Testing
- **Framework:** Vitest 1.0.4
- **DOM:** jsdom
- **Components:** React Testing Library
- **Coverage:** v8 provider

### Running Tests
```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

---

## Performance Constraints

### Hard Requirements
- **Proof Generation:** <5 seconds (hard requirement)
- **AI Processing:** <3 seconds
- **Upload:** <1 second
- **Preview:** <1 second (cached)

### Optimization Techniques
- Parallel async processing
- Image compression
- Caching generated proofs
- Connection reuse
- Efficient database queries

---

## Security Considerations

### Current (MVP)
- Input validation
- File type/size limits
- SQL injection prevention
- CORS configuration
- Error message sanitization

### Future Enhancements
- Authentication (JWT/OAuth)
- Rate limiting
- API key management
- Audit logging
- Encryption at rest

---

## Known Technical Constraints

1. **SQLite Limitations:**
   - Single connection (no true concurrency)
   - File-based (not ideal for production scale)
   - Migration path to PostgreSQL ready

2. **OpenAI API:**
   - Rate limits may require increase
   - Cost per request
   - Network latency affects performance

3. **S3 Storage:**
   - Requires AWS credentials
   - Network latency for uploads
   - Cost per GB stored

---

## Development Tools

### Required Tools
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Git
- AWS CLI (for deployment)

### Recommended Tools
- VS Code / Cursor
- Postman / Insomnia (API testing)
- Docker Desktop
- Git client

---

## Configuration Files

### Backend
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container definition
- `pytest.ini` - Test configuration
- `.env` - Environment variables (not in repo)

### Frontend
- `package.json` - Node dependencies
- `vite.config.js` - Vite configuration
- `tailwind.config.js` - Tailwind CSS config
- `Dockerfile` - Container definition

### Root
- `docker-compose.yml` - Multi-container setup
- `.gitignore` - Git ignore rules
- `README.md` - Project documentation

---

## Troubleshooting Resources

### Diagnostic Tools
- `backend/check_setup.py` - Configuration checker
- Health check endpoint: `/health`
- Backend logs: `docker-compose logs backend`
- Frontend console: Browser DevTools

### Common Issues
- Database connection errors → Check connection management
- S3 upload failures → Verify credentials and bucket
- CORS errors → Check ALLOWED_ORIGINS configuration
- AI processing timeouts → Check OpenAI API limits

