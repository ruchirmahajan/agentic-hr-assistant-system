# HR Assistant System Test Script
# Run this script to test your HR Assistant system

Write-Host "🚀 HR Assistant System Test" -ForegroundColor Green
Write-Host "=" * 50

# Check if Docker is running
Write-Host "`n🐳 Checking Docker services..." -ForegroundColor Yellow
try {
    $dockerOutput = docker-compose ps 2>&1
    if ($dockerOutput -match "hr_api.*Up") {
        Write-Host "✅ Docker services are running" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker services not running. Please run: docker-compose up -d" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error checking Docker: $_" -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host "`n⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test 1: Health Check
Write-Host "`n🔍 Testing health check..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 10
    if ($response.status -eq "healthy") {
        Write-Host "✅ Health check passed: $($response.status)" -ForegroundColor Green
    } else {
        Write-Host "❌ Health check failed: unexpected status" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Health check error: $_" -ForegroundColor Red
}

# Test 2: API Documentation
Write-Host "`n📚 Testing API documentation..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API documentation is accessible" -ForegroundColor Green
        Write-Host "   📖 Open in browser: http://localhost:8000/docs"
    } else {
        Write-Host "❌ API docs failed: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ API docs error: $_" -ForegroundColor Red
}

# Test 3: Authentication requirement
Write-Host "`n🔐 Testing authentication requirement..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/candidates/" -Method GET -TimeoutSec 10 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 401) {
        Write-Host "✅ Authentication properly required" -ForegroundColor Green
    } else {
        Write-Host "❌ Authentication test failed: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    $errorResponse = $_.Exception.Response
    if ($errorResponse.StatusCode -eq 401) {
        Write-Host "✅ Authentication properly required" -ForegroundColor Green
    } else {
        Write-Host "❌ Authentication test error: $_" -ForegroundColor Red
    }
}

# Test 4: MinIO Console
Write-Host "`n🗄️ Testing MinIO console..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9001" -Method GET -TimeoutSec 10 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ MinIO console is accessible" -ForegroundColor Green
        Write-Host "   🗄️ Open in browser: http://localhost:9001"
    } else {
        Write-Host "❌ MinIO console failed: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ MinIO console error: $_" -ForegroundColor Red
}

# Test 5: Database Connection
Write-Host "`n🗃️ Testing database connection..." -ForegroundColor Cyan
try {
    $dbTest = docker-compose exec -T postgres psql -U hr_admin -d hr_assistant_db -c "SELECT 1;" 2>&1
    if ($dbTest -match "1") {
        Write-Host "✅ Database connection successful" -ForegroundColor Green
    } else {
        Write-Host "❌ Database connection failed" -ForegroundColor Red
        Write-Host "   Output: $dbTest"
    }
} catch {
    Write-Host "❌ Database test error: $_" -ForegroundColor Red
}

# Create test data
Write-Host "`n📝 Creating test data..." -ForegroundColor Yellow
$testResume = @"
John Doe
Senior Software Engineer
Email: john.doe@example.com
Phone: +1234567890

EXPERIENCE:
• 8 years of Python development
• FastAPI and Django expertise
• PostgreSQL database design
• AWS cloud deployment
• Team leadership experience

SKILLS:
• Python, JavaScript, TypeScript
• FastAPI, React, Vue.js
• PostgreSQL, Redis, MongoDB
• Docker, Kubernetes, AWS
• Machine Learning, Data Science

EDUCATION:
• Master of Science in Computer Science
• Stanford University, 2015
"@

$testResume | Out-File -FilePath "test_resume.txt" -Encoding UTF8
Write-Host "Created test resume: test_resume.txt" -ForegroundColor Green

# Summary
Write-Host "`n" + "=" * 50 -ForegroundColor Green
Write-Host "🎯 Test Summary Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. 📖 Open API docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "2. 🗄️ Access MinIO: http://localhost:9001" -ForegroundColor White
Write-Host "3. 🔧 Run database migrations: alembic upgrade head" -ForegroundColor White
Write-Host "4. 🧪 Run full tests: pytest tests/ -v" -ForegroundColor White
Write-Host ""
Write-Host "Troubleshooting:" -ForegroundColor Yellow
Write-Host "• Check logs: docker-compose logs -f" -ForegroundColor White
Write-Host "• Restart services: docker-compose restart" -ForegroundColor White
Write-Host "• View guide: TESTING_GUIDE.md" -ForegroundColor White

# Show service status
Write-Host "`n📊 Current Service Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host "`nSystem test completed!" -ForegroundColor Green