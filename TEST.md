# 🧪 HR Assistant - Test Documentation

<div align="center">

![Testing](https://img.shields.io/badge/tests-pytest-green.svg)
![Coverage](https://img.shields.io/badge/coverage-80%25+-blue.svg)
![Status](https://img.shields.io/badge/status-passing-brightgreen.svg)

**Comprehensive test documentation for the Agentic HR Assistant application**

</div>

---

## 📋 Table of Contents

- [Test Overview](#-test-overview)
- [Test Structure](#-test-structure)
- [Running Tests](#-running-tests)
- [Test Categories](#-test-categories)
- [Unit Tests](#-unit-tests)
- [Integration Tests](#-integration-tests)
- [API Endpoint Tests](#-api-endpoint-tests)
- [Manual Test Cases](#-manual-test-cases)
- [Test Data](#-test-data)
- [Coverage Reports](#-coverage-reports)
- [CI/CD Integration](#-cicd-integration)

---

## 🎯 Test Overview

The HR Assistant application uses a comprehensive testing strategy that includes:

| Test Type | Framework | Purpose |
|-----------|-----------|---------|
| Unit Tests | pytest | Test individual functions and methods |
| Integration Tests | pytest-asyncio | Test component interactions |
| API Tests | httpx / TestClient | Test REST API endpoints |
| Manual Tests | Browser/Postman | UI and workflow validation |

### Testing Philosophy

- **Test-Driven Development (TDD)**: Tests are written alongside features
- **High Coverage**: Aim for 80%+ code coverage
- **Isolation**: Each test is independent and can run in any order
- **Async Support**: Full support for async/await testing

---

## 📁 Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_candidates.py       # Candidate API tests
├── test_jobs.py             # Job management tests (planned)
├── test_applications.py     # Application workflow tests (planned)
├── test_interviews.py       # Interview scheduling tests (planned)
├── test_documents.py        # Document upload tests (planned)
├── test_panels.py           # Interview panel tests (planned)
└── test_gdpr.py             # GDPR compliance tests (planned)
```

---

## 🚀 Running Tests

### Prerequisites

```powershell
# Install test dependencies
pip install pytest pytest-asyncio httpx pytest-cov

# Ensure server is running for integration tests
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

### Run All Tests

```powershell
# Navigate to project directory
cd "c:\Users\LENOVO\OneDrive\Documents\Python\Agentic HR Assistant"

# Run all tests with verbose output
pytest tests/ -v

# Run with detailed output
pytest tests/ -v --tb=short
```

### Run Specific Test Files

```powershell
# Run candidate tests only
pytest tests/test_candidates.py -v

# Run a specific test class
pytest tests/test_candidates.py::TestCandidateAPI -v

# Run a specific test method
pytest tests/test_candidates.py::TestCandidateAPI::test_create_candidate_success -v
```

### Run Tests by Marker

```powershell
# Run only async tests
pytest tests/ -m asyncio -v

# Run integration tests
pytest tests/ -m integration -v

# Run unit tests (exclude integration)
pytest tests/ -m "not integration" -v
```

### Run with Coverage

```powershell
# Generate coverage report
pytest tests/ --cov=src --cov-report=html

# View coverage in terminal
pytest tests/ --cov=src --cov-report=term-missing

# Generate XML coverage for CI
pytest tests/ --cov=src --cov-report=xml
```

---

## 📂 Test Categories

### 1. Candidate API Tests (`test_candidates.py`)

| Test Class | Test Method | Description | Status |
|------------|-------------|-------------|--------|
| `TestCandidateAPI` | `test_create_candidate_success` | Create candidate with valid data | ✅ |
| `TestCandidateAPI` | `test_create_candidate_missing_auth` | Verify auth requirement | ✅ |
| `TestCandidateAPI` | `test_list_candidates` | List all candidates | ✅ |
| `TestCandidateAPI` | `test_get_candidate_not_found` | Handle missing candidate | ✅ |

### 2. File Upload Tests (`TestFileUpload`)

| Test Method | Description | Expected Result | Status |
|-------------|-------------|-----------------|--------|
| `test_upload_valid_file` | Upload valid resume file | 201 Created | ✅ |
| `test_upload_invalid_file_type` | Reject .exe files | 400/500 Error | ✅ |
| `test_upload_large_file` | Reject files > 15MB | 400/500 Error | ✅ |

### 3. GDPR Compliance Tests (`TestGDPRCompliance`)

| Test Method | Description | Expected Result | Status |
|-------------|-------------|-----------------|--------|
| `test_export_candidate_data` | Export user data | JSON export | ✅ |
| `test_delete_candidate_gdpr` | Right to erasure | Data deleted | ✅ |

### 4. Integration Tests (`TestIntegrationFlow`)

| Test Method | Description | Workflow | Status |
|-------------|-------------|----------|--------|
| `test_complete_candidate_workflow` | Full CRUD cycle | Create → Get → Update → Delete | ✅ |

---

## 🔬 Unit Tests

### Test Fixtures (conftest.py)

```python
# Database Session Fixture
@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSessionLocal() as session:
        yield session

# Test Client Fixture
@pytest.fixture
def client(override_get_db) -> TestClient:
    """Create a test client."""
    return TestClient(app)

# Async Client Fixture
@pytest.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Test User Fixture
@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user with HR Manager role."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=security_utils.hash_password("testpassword123"),
        role=UserRole.HR_MANAGER,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    return user
```

### Test Data Factory

```python
class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def candidate_data() -> dict:
        return {
            "first_name": "John",
            "last_name": "Doe",
            "email": f"john.doe.{uuid4().hex[:8]}@example.com",
            "phone": "+91 98765 43210",
            "skills": "Python, FastAPI, PostgreSQL",
            "experience_years": 5,
            "education": "B.Tech Computer Science"
        }
    
    @staticmethod
    def job_data() -> dict:
        return {
            "title": "Senior Python Developer",
            "department": "Engineering",
            "location": "Bangalore",
            "employment_type": "full_time",
            "experience_required": "3-5 years",
            "salary_range": "15-25 LPA"
        }
```

---

## 🔗 Integration Tests

### Complete Candidate Workflow Test

```python
@pytest.mark.integration
class TestIntegrationFlow:
    """Integration tests for complete workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_candidate_workflow(
        self, 
        async_client: AsyncClient,
        auth_headers: dict,
        sample_resume_file: str
    ):
        """Test complete candidate management workflow."""
        
        # Step 1: Create candidate
        with open(sample_resume_file, 'rb') as f:
            files = {"resume_file": ("resume.txt", f, "text/plain")}
            create_response = await async_client.post(
                "/api/v1/candidates/",
                data=candidate_data,
                files=files,
                headers=auth_headers
            )
        
        assert create_response.status_code == status.HTTP_201_CREATED
        candidate_id = create_response.json()["id"]
        
        # Step 2: Get candidate details
        get_response = await async_client.get(
            f"/api/v1/candidates/{candidate_id}",
            headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_200_OK
        
        # Step 3: Update candidate
        update_response = await async_client.put(
            f"/api/v1/candidates/{candidate_id}",
            json={"notes": "Updated via test"},
            headers=auth_headers
        )
        assert update_response.status_code == status.HTTP_200_OK
        
        # Step 4: Delete candidate
        delete_response = await async_client.delete(
            f"/api/v1/candidates/{candidate_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == status.HTTP_200_OK
```

---

## 🌐 API Endpoint Tests

### Testing All Demo Endpoints

| Endpoint | Method | Test Case | Expected Status |
|----------|--------|-----------|-----------------|
| `/api/v1/demo/candidates` | GET | List all candidates | 200 OK |
| `/api/v1/demo/candidates` | POST | Create new candidate | 201 Created |
| `/api/v1/demo/candidates/{id}` | GET | Get candidate by ID | 200 OK |
| `/api/v1/demo/candidates/{id}` | PUT | Update candidate | 200 OK |
| `/api/v1/demo/candidates/{id}` | DELETE | Delete candidate | 200 OK |
| `/api/v1/demo/jobs` | GET | List all jobs | 200 OK |
| `/api/v1/demo/jobs` | POST | Create new job | 201 Created |
| `/api/v1/demo/panels` | GET | List panels | 200 OK |
| `/api/v1/demo/panels` | POST | Create panel | 201 Created |
| `/api/v1/demo/slots` | GET | List slots | 200 OK |
| `/api/v1/demo/slots` | POST | Create slot | 201 Created |
| `/api/v1/demo/interviews` | GET | List interviews | 200 OK |
| `/api/v1/demo/interviews` | POST | Schedule interview | 201 Created |
| `/api/v1/demo/candidates/{id}/documents` | GET | List documents | 200 OK |
| `/api/v1/demo/candidates/{id}/documents` | POST | Upload document | 201 Created |
| `/api/v1/demo/documents/{id}` | GET | Get document | 200 OK |
| `/api/v1/demo/documents/{id}/download` | GET | Download document | 200 OK |
| `/api/v1/demo/documents/{id}/verify` | PUT | Verify document | 200 OK |

### Sample API Test

```python
@pytest.mark.asyncio
async def test_create_job(async_client: AsyncClient, auth_headers: dict):
    """Test job creation endpoint."""
    job_data = {
        "title": "Python Developer",
        "department": "Engineering",
        "location": "Remote",
        "employment_type": "full_time",
        "experience_required": "2-4 years",
        "description": "We are looking for a Python developer...",
        "requirements": "Python, FastAPI, PostgreSQL"
    }
    
    response = await async_client.post(
        "/api/v1/demo/jobs",
        json=job_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    result = response.json()
    assert "id" in result
    assert result["title"] == job_data["title"]
```

---

## 📝 Manual Test Cases

### Dashboard Functionality Tests

| Test ID | Feature | Steps | Expected Result | Status |
|---------|---------|-------|-----------------|--------|
| TC-001 | Dashboard Load | Open http://127.0.0.1:8000/dashboard | Dashboard displays with stats | ✅ |
| TC-002 | Add Candidate | Click "Add Candidate" → Fill form → Submit | Candidate created, appears in list | ✅ |
| TC-003 | View Candidate | Click "View" on candidate card | Modal shows candidate details | ✅ |
| TC-004 | Edit Candidate | Click "Edit" → Modify → Save | Changes saved successfully | ✅ |
| TC-005 | Delete Candidate | Click delete → Confirm | Candidate removed from list | ✅ |
| TC-006 | Add Job | Navigate to Jobs → Add Job | Job created successfully | ✅ |
| TC-007 | Upload Document | Candidate → Documents → Upload | Document uploaded, appears in list | ✅ |
| TC-008 | Verify Document | Click Verify → Set status | Status updated | ✅ |
| TC-009 | Create Panel | Panels tab → Create Panel | Panel created | ✅ |
| TC-010 | Create Slot | Slots tab → Add Slot | Slot created | ✅ |
| TC-011 | Schedule Interview | Interviews → Schedule | Interview scheduled | ✅ |

### Document Upload Test Cases

| Test ID | Document Type | File Type | Size | Expected | Status |
|---------|---------------|-----------|------|----------|--------|
| DOC-001 | Resume | PDF | 2MB | Success | ✅ |
| DOC-002 | Resume | DOCX | 1MB | Success | ✅ |
| DOC-003 | Identity Proof | JPG | 500KB | Success | ✅ |
| DOC-004 | Certificate | PNG | 3MB | Success | ✅ |
| DOC-005 | Invalid | EXE | 1MB | Rejected | ✅ |
| DOC-006 | Large File | PDF | 20MB | Rejected (>15MB) | ✅ |

### Interview Panel Test Cases

| Test ID | Action | Input | Expected Result | Status |
|---------|--------|-------|-----------------|--------|
| PNL-001 | Create Panel | Valid data | Panel created | ✅ |
| PNL-002 | Add Members | JSON array | Members added | ✅ |
| PNL-003 | Update Panel | Modified data | Panel updated | ✅ |
| PNL-004 | Delete Panel | Panel ID | Panel deleted | ✅ |
| PNL-005 | List Panels | No params | All panels returned | ✅ |

---

## 📊 Test Data

### Sample Test Candidates

```json
[
  {
    "first_name": "Ruchir",
    "last_name": "Mahajan",
    "email": "ruchir.mahajan@example.com",
    "phone": "+91 98765 43210",
    "skills": "Python, FastAPI, React, PostgreSQL",
    "experience_years": 4,
    "education": "B.Tech Computer Science, IIT Delhi"
  },
  {
    "first_name": "Nitesh",
    "last_name": "Mahajan",
    "email": "nitesh.mahajan@gmail.com",
    "phone": "+91 98765 43211",
    "skills": "Java, Spring Boot, Microservices",
    "experience_years": 6,
    "education": "MCA, Delhi University"
  }
]
```

### Sample Test Jobs

```json
[
  {
    "title": "Senior Python Developer",
    "department": "Engineering",
    "location": "Bangalore, India",
    "employment_type": "full_time",
    "experience_required": "3-5 years",
    "salary_range": "15-25 LPA",
    "description": "Looking for experienced Python developers...",
    "requirements": "Python, FastAPI, PostgreSQL, Docker, AWS"
  }
]
```

### Sample Test Documents

| Document Type | Test File | Purpose |
|---------------|-----------|---------|
| Resume | `test_resume.pdf` | Resume upload testing |
| Identity | `test_id.jpg` | Identity proof testing |
| Certificate | `test_cert.pdf` | Education cert testing |

---

## 📈 Coverage Reports

### Generate Coverage Report

```powershell
# Run tests with coverage
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Open HTML report
start htmlcov/index.html
```

### Expected Coverage

| Module | Coverage | Status |
|--------|----------|--------|
| `src/api/demo.py` | 85% | ✅ |
| `src/models/` | 90% | ✅ |
| `src/services/` | 75% | ⚠️ |
| `src/core/` | 80% | ✅ |
| **Overall** | **82%** | ✅ |

---

## 🔄 CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov httpx
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: coverage.xml
```

---

## 🐛 Debugging Tests

### Common Issues

#### 1. Database Connection Errors
```powershell
# Ensure database exists
python init_db.py

# Check database file
Test-Path hr_assistant.db
```

#### 2. Import Errors
```powershell
# Verify Python path
$env:PYTHONPATH = "."
pytest tests/ -v
```

#### 3. Async Test Failures
```python
# Ensure proper async markers
@pytest.mark.asyncio
async def test_async_function():
    ...
```

#### 4. Fixture Not Found
```python
# Check fixture scope and imports in conftest.py
@pytest.fixture(scope="function")
def my_fixture():
    ...
```

### Debug Mode

```powershell
# Run with debug output
pytest tests/ -v -s --tb=long

# Run specific test with debugging
pytest tests/test_candidates.py::TestCandidateAPI::test_create_candidate_success -v -s
```

---

## 📋 Test Checklist

### Before Release

- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Coverage > 80%
- [ ] No critical/high severity issues
- [ ] API documentation updated
- [ ] Manual smoke tests completed

### Manual Smoke Test Checklist

- [ ] Server starts without errors
- [ ] Dashboard loads correctly
- [ ] Can create/edit/delete candidates
- [ ] Can create/edit/delete jobs
- [ ] Document upload works
- [ ] Interview scheduling works
- [ ] All modals open correctly
- [ ] No JavaScript console errors

---

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [httpx Documentation](https://www.python-httpx.org/)

---

<div align="center">

**Happy Testing! 🧪**

</div>
