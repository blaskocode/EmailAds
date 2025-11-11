# System Patterns: HiBid Email MVP

---

## Architecture Overview

```
Frontend (React) → Backend API (FastAPI) → Services Layer → External APIs
                                      ↓
                                  Database (SQLite)
                                  S3 Storage (AWS)
```

---

## Key Design Patterns

### 1. Service Layer Pattern

All business logic is encapsulated in service classes:
- `ai_service.py` - OpenAI integration
- `campaign_service.py` - Database operations
- `file_service.py` - File handling
- `image_service.py` - Image processing
- `proof_service.py` - Proof generation
- `s3_service.py` - AWS S3 operations
- `template_service.py` - Email template rendering

**Benefits:**
- Separation of concerns
- Testability
- Reusability

### 2. Dependency Injection

FastAPI dependencies used for:
- Database connections (`get_db()`)
- Service initialization
- Request validation

**Pattern:**
```python
async def endpoint(conn = Depends(get_db)):
    # Use conn for database operations
```

### 3. Async/Await Pattern

All I/O operations are async:
- Database queries (aiosqlite)
- S3 uploads (boto3 in thread pool)
- OpenAI API calls
- File operations

**Benefits:**
- Non-blocking operations
- Better performance
- Concurrent processing

### 4. Error Handling Strategy

**Layered Error Handling:**
1. **Route Level:** Catch HTTPException, re-raise
2. **Service Level:** Catch specific errors, convert to HTTPException
3. **Global Level:** Catch-all exception handler

**Custom Exceptions:**
- `CampaignNotFoundError`
- `CampaignStateError`
- `S3Error`
- `AIProcessingError`

### 5. Database Connection Management

**Pattern:** Single global connection with validation
- Connection initialized at startup
- Reconnected if closed
- Shared across requests (SQLite limitation)
- Future: Connection pooling for PostgreSQL

### 6. File Upload Pattern

**Multi-step Process:**
1. Validate file type and size
2. Read file content
3. Check if updating existing campaign (if campaign_id provided)
4. Upload to S3
5. Store metadata in database
6. Return campaign ID

**Update vs Create:**
- If `campaign_id` provided and campaign exists with status 'rejected', update existing campaign
- Otherwise, create new campaign
- When updating: reset status to 'uploaded', clear old proof/HTML paths, save all metadata changes

**Error Recovery:**
- Validation errors return 400 immediately
- S3 errors logged and returned as 500
- Database errors trigger reconnection

### 7. AI Processing Pattern

**Parallel Processing:**
- Text and image processing run concurrently
- `asyncio.gather()` for parallel execution
- Timeout handling (10 sec max)
- Fallback for AI failures

### 8. Template Rendering Pattern

**MJML → HTML Pipeline:**
1. Load MJML template
2. Inject campaign data
3. Compile to HTML
4. Inline CSS (Premailer)
5. Return production-ready HTML

---

## Component Relationships

### Backend Structure

```
app/
├── main.py           # FastAPI app, routing, middleware
├── config.py         # Settings (Pydantic BaseSettings)
├── database.py       # Connection management
├── models/           # Data models (Campaign, Schemas)
├── routes/           # API endpoints (6 routes)
├── services/         # Business logic (7 services)
├── utils/            # Helpers (validators, error handlers)
└── templates/        # MJML email template
```

### Frontend Structure

```
src/
├── App.jsx           # Router configuration
├── pages/            # Route components (3 pages)
├── components/       # Reusable components (10+)
├── services/         # API client (api.js)
├── contexts/         # React contexts (Toast)
└── utils/            # Helper functions
```

---

## Data Flow Patterns

### Upload Flow
```
Client → Upload Route → File Service → S3 Service → Campaign Service → Database
```

### Processing Flow
```
Client → Process Route → AI Service (parallel) → Image Service → Campaign Service
```

### Preview Flow
```
Client → Preview Route → Campaign Service → Proof Service → Template Service → Response
```

---

## State Management

### Backend State
- **Campaign Status:** `uploaded → processed → ready → approved/rejected`
- **Database:** SQLite with status tracking
- **S3:** Asset storage with metadata

### Frontend State
- **React State:** Component-level state management
- **Context API:** Toast notifications
- **No Global State:** Simple state management for MVP

---

## Security Patterns

### Input Validation
- File type validation (whitelist)
- File size limits (5MB)
- Text length limits
- SQL injection prevention (parameterized queries)

### Error Messages
- User-friendly error messages
- No sensitive information exposed
- Detailed logging for debugging

### CORS Configuration
- Allowed origins from environment
- Credentials enabled
- All methods and headers allowed

---

## Performance Patterns

### Optimization Strategies
1. **Parallel Processing:** AI calls run concurrently
2. **Caching:** Generated proofs cached in S3
3. **Async Operations:** Non-blocking I/O
4. **Image Optimization:** Resize and compress before upload
5. **Connection Reuse:** Single database connection

### Performance Targets
- Upload: <1 second
- Process: <5 seconds (hard requirement)
- Generate: <2 seconds
- Preview: <1 second (cached)

---

## Testing Patterns

### Backend Testing
- **Unit Tests:** Service functions, utilities
- **Integration Tests:** API endpoints
- **Fixtures:** Mock S3, OpenAI, database
- **Coverage:** Target >60%

### Frontend Testing
- **Component Tests:** React Testing Library
- **API Tests:** Mock axios responses
- **Setup:** Vitest with jsdom

---

## Deployment Patterns

### Docker Strategy
- Multi-stage builds
- Separate containers for frontend/backend
- docker-compose for local development
- Production-ready Dockerfiles

### Environment Management
- `.env` files for configuration
- Pydantic Settings for validation
- Environment-specific configs

---

## Known Patterns & Conventions

### Naming Conventions
- **Routes:** `verb_noun.py` (e.g., `upload.py`, `process.py`)
- **Services:** `noun_service.py` (e.g., `ai_service.py`)
- **Models:** `noun.py` (e.g., `campaign.py`)
- **Utils:** `purpose_utils.py` (e.g., `image_utils.py`)

### Code Organization
- **Routes:** Thin controllers, delegate to services
- **Services:** Business logic, no HTTP concerns
- **Models:** Data structures and database operations
- **Utils:** Pure functions, no side effects

### Error Handling Convention
```python
try:
    # Operation
except SpecificError:
    raise HTTPException(status_code=400, detail="...")
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="...")
```

---

## Future Architecture Considerations

### Scalability
- **Database:** Migration to PostgreSQL with connection pooling
- **Caching:** Redis for frequently accessed data
- **Queue System:** SQS/Celery for async processing
- **Load Balancing:** Multiple backend instances

### Monitoring
- **Logging:** Structured logging to CloudWatch
- **Metrics:** Application performance monitoring
- **Alerts:** Error rate and latency monitoring

### Security Enhancements
- **Authentication:** JWT/OAuth implementation
- **Rate Limiting:** Per-user rate limits
- **API Keys:** Key management system
- **Audit Logging:** Track all operations

