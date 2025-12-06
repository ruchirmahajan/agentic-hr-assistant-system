# Simple HR Assistant System Test
# Run this to test your system

Write-Host "HR Assistant System Test" -ForegroundColor Green
Write-Host "========================"

# Check Docker services
Write-Host "`nChecking Docker services..." -ForegroundColor Yellow
try {
    $dockerOutput = docker-compose ps
    if ($dockerOutput -match "hr_api.*Up") {
        Write-Host "SUCCESS: Docker services are running" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Docker services not running" -ForegroundColor Red
        Write-Host "Please run: docker-compose up -d" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "ERROR: Cannot check Docker status" -ForegroundColor Red
    exit 1
}

# Test health endpoint
Write-Host "`nTesting health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 10
    if ($response.status -eq "healthy") {
        Write-Host "SUCCESS: Health check passed" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Health check failed" -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR: Cannot connect to API" -ForegroundColor Red
    Write-Host "Make sure services are running and try again" -ForegroundColor Yellow
}

# Test API documentation
Write-Host "`nTesting API documentation..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "SUCCESS: API docs accessible" -ForegroundColor Green
        Write-Host "Open in browser: http://localhost:8000/docs" -ForegroundColor Cyan
    }
} catch {
    Write-Host "ERROR: API docs not accessible" -ForegroundColor Red
}

# Test MinIO console
Write-Host "`nTesting MinIO console..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9001" -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "SUCCESS: MinIO console accessible" -ForegroundColor Green
        Write-Host "Open in browser: http://localhost:9001" -ForegroundColor Cyan
    }
} catch {
    Write-Host "ERROR: MinIO console not accessible" -ForegroundColor Red
}

# Test database
Write-Host "`nTesting database..." -ForegroundColor Yellow
try {
    $dbTest = docker-compose exec -T postgres psql -U hr_admin -d hr_assistant_db -c "SELECT 1;" 2>&1
    if ($dbTest -match "1") {
        Write-Host "SUCCESS: Database connection works" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Database connection failed" -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR: Cannot test database" -ForegroundColor Red
}

# Show service status
Write-Host "`nCurrent Service Status:" -ForegroundColor Cyan
docker-compose ps

Write-Host "`nTest completed!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Check API docs: http://localhost:8000/docs"
Write-Host "2. Access MinIO: http://localhost:9001"
Write-Host "3. Run migrations: alembic upgrade head"
Write-Host "4. Install Python deps: pip install -r requirements.txt"