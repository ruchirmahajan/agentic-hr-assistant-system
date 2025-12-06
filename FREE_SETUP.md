# Free Open Source HR Assistant Setup

This configuration uses only FREE and OPEN SOURCE alternatives - no paid APIs required!

## Required Environment Variables (.env)

```env
# Database (Free PostgreSQL)
DATABASE_URL=postgresql://hr_admin:your_secure_password@localhost:5432/hr_assistant_db

# Local File Storage (instead of paid MinIO/S3)
STORAGE_TYPE=local
STORAGE_PATH=./storage
UPLOAD_PATH=./uploads

# Security (Generate your own keys)
SECRET_KEY=your-32-character-or-longer-secret-key-here-free
ENCRYPTION_KEY=XMdTgOirdSWdwDxqTE_U84DMvHTehyAcK5_UJIkGPy4=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

# Free Local AI Options (pick one)
# Option 1: Ollama (recommended - completely free)
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Option 2: LocalAI (free alternative to OpenAI)
# AI_PROVIDER=localai
# LOCAL_AI_BASE_URL=http://localhost:8080/v1
# LOCAL_AI_MODEL=ggml-model-q4_0

# Option 3: Rule-based (no AI, just text processing)
# AI_PROVIDER=rules

# Optional Redis (free local install)
REDIS_URL=redis://localhost:6379
# REDIS_PASSWORD=optional

# Application Settings
APP_NAME=Agentic HR Assistant
APP_VERSION=1.0.0
API_PREFIX=/api/v1
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# GDPR Settings
DATA_RETENTION_YEARS=7
CONSENT_REQUIRED=true
AUDIT_LOG_RETENTION_YEARS=10

# File Upload Settings
MAX_FILE_SIZE_MB=10
ALLOWED_EXTENSIONS=[".pdf", ".doc", ".docx", ".txt"]
```

## Free Service Setup Instructions

### 1. PostgreSQL (Free Database)
```bash
# Install PostgreSQL locally (free)
# Windows: Download from postgresql.org
# Create database:
createdb hr_assistant_db
```

### 2. Ollama (Free AI - Recommended)
```bash
# Install Ollama (completely free)
# Visit: https://ollama.ai/download
# Pull a model:
ollama pull llama2
```

### 3. Redis (Optional - Free Caching)
```bash
# Install Redis locally (optional but recommended)
# Windows: Download from redis.io
```

## NO PAID SERVICES REQUIRED:
- ❌ NO Anthropic Claude API ($)
- ❌ NO OpenAI API ($)
- ❌ NO AWS S3 ($)
- ❌ NO Cloud databases ($)
- ❌ NO MinIO Cloud ($)

## WHAT YOU GET FOR FREE:
- ✅ Full HR management system
- ✅ Resume parsing and analysis
- ✅ Interview question generation
- ✅ Candidate assessment
- ✅ File upload and storage
- ✅ GDPR compliance features
- ✅ REST API
- ✅ Admin dashboard

## Quick Start (All Free):
1. Install PostgreSQL locally
2. Install Ollama and pull llama2 model
3. Copy the .env configuration above
4. Run: `python -m uvicorn src.main:app --reload`

Total cost: $0.00 💰