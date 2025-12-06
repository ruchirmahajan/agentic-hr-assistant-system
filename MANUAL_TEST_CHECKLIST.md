# 🧪 Manual Testing Checklist for HR Assistant

## Pre-Test Setup

- [ ] **Environment Setup**
  ```powershell
  # Copy .env.example to .env
  cp .env.example .env
  
  # Edit .env with your settings:
  # - ANTHROPIC_API_KEY=your_key_here
  # - SECRET_KEY=your_32_char_secret
  # - ENCRYPTION_KEY=your_32_char_key
  ```

- [ ] **Start Services**
  ```powershell
  docker-compose up -d
  ```

- [ ] **Wait for startup (60 seconds)**

## 🔍 Basic System Tests

### 1. Health Check
- [ ] Visit: http://localhost:8000/health
- [ ] Expected: `{"status": "healthy", ...}`

### 2. API Documentation  
- [ ] Visit: http://localhost:8000/docs
- [ ] Expected: Interactive Swagger UI
- [ ] Try the "Health Check" endpoint in the UI

### 3. Service Status
```powershell
# Check all services are running
docker-compose ps

# Expected output should show all services as "Up"
```

## 🗄️ Storage Systems

### 4. MinIO Object Storage
- [ ] Visit: http://localhost:9001
- [ ] Login with credentials from .env file
- [ ] Buckets should exist: `hr-resumes`, `hr-documents`

### 5. PostgreSQL Database
```powershell
# Connect to database
docker-compose exec postgres psql -U hr_admin -d hr_assistant_db

# Check schemas exist
\dn

# Check tables exist
\dt hr_core.*

# Exit with \q
```

## 🔐 Security Tests

### 6. Authentication Required
```powershell
# This should return 401 Unauthorized
curl http://localhost:8000/api/v1/candidates/
```

### 7. CORS Headers
```powershell
# Check CORS configuration
curl -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" -X OPTIONS http://localhost:8000/api/v1/candidates/
```

## 📁 File Upload Tests

### 8. Create Test Files

```powershell
# Create valid resume
@"
Jane Smith
Software Engineer
Email: jane@example.com

SKILLS: Python, FastAPI, PostgreSQL
EXPERIENCE: 5 years software development
"@ | Out-File -FilePath "test_resume.txt" -Encoding UTF8

# Create invalid file
"malicious content" | Out-File -FilePath "test_malware.exe"

# Create large file (>10MB)
"x" * (11 * 1024 * 1024) | Out-File -FilePath "large_file.txt"
```

### 9. Test File Validation (via API docs)
- [ ] Go to http://localhost:8000/docs
- [ ] Find "POST /api/v1/candidates/"
- [ ] Try uploading `test_resume.txt` (should work)
- [ ] Try uploading `test_malware.exe` (should be rejected)
- [ ] Try uploading `large_file.txt` (should be rejected)

## 🤖 AI Integration Tests

### 10. Anthropic Claude API
Create test script:
```powershell
# Save as test_claude.py
@"
import asyncio
from src.services.claude_service import claude_service

async def test_claude():
    try:
        skills = await claude_service.extract_skills_from_resume("Python FastAPI PostgreSQL experience")
        print(f"Skills extracted: {skills}")
    except Exception as e:
        print(f"Claude error: {e}")

asyncio.run(test_claude())
"@ | Out-File -FilePath "test_claude.py"

# Run the test
python test_claude.py
```

## 📊 Database Tests

### 11. Data Encryption Verification
```powershell
# Connect to database
docker-compose exec postgres psql -U hr_admin -d hr_assistant_db

# Create test candidate (this would normally be done via API)
# Check that PII fields are encrypted
SELECT id, length(encrypted_email), length(encrypted_full_name) FROM hr_core.candidates LIMIT 5;
```

### 12. Schema Validation
```powershell
# Verify all required tables exist
docker-compose exec postgres psql -U hr_admin -d hr_assistant_db -c "
SELECT schemaname, tablename 
FROM pg_tables 
WHERE schemaname IN ('hr_core', 'hr_audit', 'hr_analytics')
ORDER BY schemaname, tablename;
"
```

## 🚨 Error Handling Tests

### 13. Database Failure Recovery
```powershell
# Stop database
docker-compose stop postgres

# Try API call (should handle gracefully)
curl http://localhost:8000/health

# Restart database  
docker-compose start postgres
```

### 14. MinIO Failure Recovery
```powershell
# Stop MinIO
docker-compose stop minio

# Try file operation (should return appropriate error)
# Restart MinIO
docker-compose start minio
```

## 🔧 Migration Tests

### 15. Database Migrations
```powershell
# Install alembic if not already installed
pip install alembic

# Run migrations
alembic upgrade head

# Check migration history
alembic history --verbose

# Downgrade (optional test)
# alembic downgrade -1
# alembic upgrade head
```

## 📈 Performance Tests

### 16. Load Testing
```powershell
# Simple load test
for ($i=1; $i -le 10; $i++) {
    $response = Invoke-RestMethod "http://localhost:8000/health"
    Write-Host "Request $i: $($response.status)"
}
```

### 17. Memory Usage
```powershell
# Check container resource usage
docker stats --no-stream
```

## 🎯 End-to-End Workflow Test

### 18. Complete User Journey (Manual)
1. [ ] Open API docs at http://localhost:8000/docs
2. [ ] Create a test user (via database or implement auth endpoint)
3. [ ] Get authentication token
4. [ ] Create candidate with resume upload
5. [ ] Verify candidate data is encrypted in database
6. [ ] Check file is stored in MinIO
7. [ ] Update candidate information
8. [ ] Export candidate data (GDPR)
9. [ ] Delete candidate (GDPR compliance)

## ✅ Success Criteria

All tests should pass with:
- [ ] Health endpoint returns 200
- [ ] API documentation loads
- [ ] Authentication is enforced
- [ ] Files upload and validate correctly
- [ ] Database operations work
- [ ] MinIO storage functions
- [ ] GDPR operations complete
- [ ] Error handling is graceful
- [ ] Performance is acceptable

## 🔧 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Connection refused" | Check `docker-compose ps`, restart services |
| "Import errors" | Run `pip install -r requirements.txt` |
| "Database not found" | Run `alembic upgrade head` |
| "MinIO access denied" | Check credentials in `.env` file |
| "Claude API errors" | Verify `ANTHROPIC_API_KEY` in `.env` |
| "Permission denied" | Check user roles and JWT token |

## 📝 Test Results Template

```
Date: ___________
Tester: ___________

Basic Tests:        ___/5 passed
Storage Tests:      ___/2 passed  
Security Tests:     ___/2 passed
File Upload Tests:  ___/3 passed
AI Integration:     ___/1 passed
Database Tests:     ___/2 passed
Error Handling:     ___/2 passed
Performance:        ___/2 passed
End-to-End:         ___/1 passed

TOTAL:             ___/20 passed

Issues Found:
1. ________________________
2. ________________________
3. ________________________

Overall Status: [ ] PASS [ ] FAIL
```