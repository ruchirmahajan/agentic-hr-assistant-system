# HR Assistant Testing Guide

## Quick Testing Setup

### 1. Install Test Dependencies

```powershell
# Navigate to project directory
cd "c:\Users\LENOVO\OneDrive\Documents\Python\Agentic HR Assistant"

# Install all dependencies including test tools
pip install -r requirements.txt

# Install additional test dependencies
pip install pytest pytest-asyncio httpx
```

### 2. Start the System

```powershell
# Start all services with Docker
docker-compose up -d

# Wait for services to be ready (30-60 seconds)
docker-compose ps

# Check service health
curl http://localhost:8000/health
```

### 3. Run Database Migrations

```powershell
# Run migrations to create tables
alembic upgrade head

# Verify database is ready
docker-compose exec postgres psql -U hr_admin -d hr_assistant_db -c "\dt hr_core.*"
```

## Testing Methods

### 🧪 Automated Tests

```powershell
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_candidates.py -v
pytest tests/ -k "test_create_candidate" -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### 🌐 Manual API Testing

#### 1. **Health Check**

```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1701851234.567,
  "version": "1.0.0",
  "environment": "development"
}
```

#### 2. **API Documentation**

Open in browser: http://localhost:8000/docs

This provides an interactive API testing interface.

#### 3. **Create Test User (Manual DB Insert)**

```powershell
# Connect to database
docker-compose exec postgres psql -U hr_admin -d hr_assistant_db

# Create a test user (in psql prompt)
INSERT INTO hr_core.users (
    id, username, email, hashed_password, first_name, last_name, 
    role, is_active, consent_status
) VALUES (
    gen_random_uuid(),
    'testuser',
    'test@example.com',
    '$2b$12$your_hashed_password_here',
    'Test',
    'User',
    'hr_manager',
    true,
    '{"data_processing": true}'::jsonb
);
```

#### 4. **Get Authentication Token**

```powershell
# This would require implementing a login endpoint
# For now, you can create a token manually using the security utils
```

### 📁 File Upload Testing

#### Create Test Files

```powershell
# Create test resume file
@"
John Doe
Senior Software Engineer
Email: john.doe@example.com
Phone: +1234567890

EXPERIENCE:
- 8 years of Python development
- FastAPI and Django expertise  
- PostgreSQL database design
- AWS cloud deployment
- Team leadership experience

SKILLS:
- Python, JavaScript, TypeScript
- FastAPI, React, Vue.js
- PostgreSQL, Redis, MongoDB  
- Docker, Kubernetes, AWS
- Machine Learning, Data Science

EDUCATION:
- Master of Science in Computer Science
- Stanford University, 2015
"@ | Out-File -FilePath "test_resume.txt" -Encoding UTF8
```

#### Test File Upload via API

```powershell
# Upload resume (requires authentication token)
curl -X POST "http://localhost:8000/api/v1/candidates/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "full_name=John Doe" \
  -F "email=john.doe@example.com" \
  -F "phone=+1234567890" \
  -F "experience_years=8" \
  -F "current_position=Senior Software Engineer" \
  -F "resume_file=@test_resume.txt"
```

### 🗄️ Database Testing

#### Verify Tables Created

```powershell
docker-compose exec postgres psql -U hr_admin -d hr_assistant_db -c "
SELECT schemaname, tablename 
FROM pg_tables 
WHERE schemaname IN ('hr_core', 'hr_audit', 'hr_analytics')
ORDER BY schemaname, tablename;
"
```

#### Check Data Encryption

```powershell
# View encrypted candidate data
docker-compose exec postgres psql -U hr_admin -d hr_assistant_db -c "
SELECT id, experience_years, current_position, 
       length(encrypted_email) as email_length,
       length(encrypted_full_name) as name_length
FROM hr_core.candidates 
LIMIT 5;
"
```

### 📦 MinIO Storage Testing

#### Access MinIO Console

1. Open http://localhost:9001 in browser
2. Login with credentials from `.env` file
3. Check if buckets `hr-resumes` and `hr-documents` exist
4. Upload test files manually to verify storage

#### Test via Command Line

```powershell
# Install MinIO client
# Download from https://min.io/download#/windows

# Configure MinIO client
mc alias set local http://localhost:9000 minioadmin your_minio_password

# List buckets
mc ls local

# Upload test file
mc cp test_resume.txt local/hr-resumes/
```

### 🤖 Anthropic Claude Testing

#### Test with Mock API

Create a test script to verify Claude integration:

```python
# test_claude.py
import asyncio
from src.services.claude_service import claude_service

async def test_claude():
    resume_text = """
    John Doe - Software Engineer
    5 years Python experience
    Skills: Python, FastAPI, PostgreSQL
    """
    
    try:
        skills = await claude_service.extract_skills_from_resume(resume_text)
        print(f"Extracted skills: {skills}")
    except Exception as e:
        print(f"Claude API error: {e}")

if __name__ == "__main__":
    asyncio.run(test_claude())
```

Run the test:
```powershell
python test_claude.py
```

### 🔐 Security Testing

#### Test Authentication

```powershell
# Test without authentication (should fail)
curl -X GET "http://localhost:8000/api/v1/candidates/"

# Expected: 401 Unauthorized
```

#### Test File Security

```powershell
# Create malicious file
echo "malicious content" | Out-File -FilePath "malware.exe"

# Try to upload (should be rejected)
curl -X POST "http://localhost:8000/api/v1/candidates/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "full_name=Test User" \
  -F "email=test@example.com" \
  -F "resume_file=@malware.exe"
```

### 📊 Performance Testing

#### Load Test with Multiple Requests

```powershell
# Install Apache Bench or use PowerShell
for ($i=1; $i -le 10; $i++) {
    Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "Request $i completed"
}
```

### 🚨 Error Scenario Testing

#### Test Database Connection Failure

```powershell
# Stop database temporarily
docker-compose stop postgres

# Try API call (should handle gracefully)
curl http://localhost:8000/api/v1/candidates/

# Restart database
docker-compose start postgres
```

#### Test MinIO Connection Failure

```powershell
# Stop MinIO
docker-compose stop minio

# Try file upload (should return appropriate error)
# Restart MinIO
docker-compose start minio
```

## Expected Test Results

### ✅ Successful Tests Should Show:

1. **Health Check**: Returns 200 with system status
2. **Database**: Tables created in correct schemas
3. **File Upload**: Files stored in MinIO buckets
4. **Security**: Unauthorized requests blocked
5. **GDPR**: Encrypted PII data in database
6. **API Documentation**: Available at /docs endpoint

### 🔍 Common Issues & Solutions

#### Issue: "Import errors" in tests
```powershell
# Solution: Install test dependencies
pip install pytest pytest-asyncio httpx
```

#### Issue: Database connection error
```powershell
# Solution: Check if PostgreSQL is running
docker-compose ps
docker-compose logs postgres
```

#### Issue: MinIO access denied
```powershell
# Solution: Verify credentials in .env file
# Check MinIO logs
docker-compose logs minio
```

#### Issue: Anthropic API errors
```powershell
# Solution: Verify API key in .env
# Check API usage limits
```

## Production Testing Checklist

- [ ] All services start successfully
- [ ] Database migrations apply without errors
- [ ] File uploads work with various formats
- [ ] Authentication and authorization work
- [ ] GDPR compliance features function
- [ ] API documentation is accessible
- [ ] Error handling is graceful
- [ ] Performance is acceptable under load
- [ ] Security measures prevent unauthorized access
- [ ] Backup and recovery procedures work

## Monitoring During Tests

### View Logs in Real-time

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f hr_api
docker-compose logs -f postgres
docker-compose logs -f minio
```

### Monitor Resource Usage

```powershell
# Container stats
docker stats

# Database connections
docker-compose exec postgres psql -U hr_admin -d hr_assistant_db -c "SELECT count(*) FROM pg_stat_activity;"
```

This comprehensive testing approach will help you verify that all components of the Agentic HR Assistant are working correctly before deploying to production.