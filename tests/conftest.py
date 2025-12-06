"""
Test configuration and utilities for HR Assistant
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os
from typing import Generator, AsyncGenerator

from src.main import app
from src.core.config import settings
from src.core.database import get_db, Base
from src.models.user import User, UserRole
from src.core.security import security_utils

# Test database URL (use separate test database)
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/hr_assistant_db", "/hr_assistant_test_db")

# Test engine and session
test_engine = create_async_engine(
    TEST_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True
)

TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override the get_db dependency for testing."""
    async def _get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client(override_get_db) -> TestClient:
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=security_utils.hash_password("testpassword123"),
        first_name="Test",
        last_name="User",
        role=UserRole.HR_MANAGER,
        is_active=True,
        consent_status={
            "data_processing": True,
            "analytics": False,
            "marketing": False
        }
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest.fixture
def auth_token(test_user: User) -> str:
    """Create an authentication token for the test user."""
    token_data = {
        "user_id": str(test_user.id),
        "username": test_user.username,
        "role": test_user.role.value
    }
    
    return security_utils.create_access_token(token_data)


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Create authentication headers."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def sample_resume_file():
    """Create a sample resume file for testing."""
    resume_content = """
    John Doe
    Software Engineer
    Email: john.doe@example.com
    Phone: +1234567890
    
    EXPERIENCE:
    - 5 years of Python development
    - Experience with FastAPI, Django
    - Database design and optimization
    - Cloud deployment (AWS, Docker)
    
    SKILLS:
    - Python, JavaScript, SQL
    - FastAPI, React, PostgreSQL
    - Docker, Kubernetes, AWS
    - Machine Learning, Data Analysis
    
    EDUCATION:
    - Bachelor of Science in Computer Science
    - University of Technology, 2019
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(resume_content)
        temp_file_path = f.name
    
    yield temp_file_path
    
    # Cleanup
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


class TestDataFactory:
    """Factory class for creating test data."""
    
    @staticmethod
    def candidate_data():
        """Generate test candidate data."""
        return {
            "full_name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "+1987654321",
            "experience_years": 3,
            "current_position": "Frontend Developer",
            "current_company": "Tech Corp",
            "source": "LinkedIn"
        }
    
    @staticmethod
    def job_data():
        """Generate test job data."""
        return {
            "title": "Senior Python Developer",
            "description": "We are looking for a senior Python developer...",
            "requirements": {
                "required_skills": ["Python", "FastAPI", "PostgreSQL"],
                "experience_years": 5,
                "education_level": "bachelor"
            },
            "department": "Engineering",
            "location": "Remote",
            "salary_range": "$80,000 - $120,000"
        }


# Mock configurations for testing
class TestConfig:
    """Test-specific configuration overrides."""
    
    # Mock Anthropic API responses
    MOCK_CLAUDE_RESPONSES = {
        "resume_analysis": {
            "overall_match_score": 85,
            "technical_skills": {
                "required_skills_match": ["Python", "FastAPI"],
                "missing_critical_skills": ["Kubernetes"],
                "additional_relevant_skills": ["React", "Docker"]
            },
            "experience_analysis": {
                "years_experience": 5,
                "relevant_experience_score": 90,
                "industry_match": True,
                "role_progression": "senior"
            },
            "education_analysis": {
                "degree_relevance": 95,
                "certifications": ["AWS Certified"],
                "education_level": "bachelor"
            },
            "strengths": [
                "Strong Python skills",
                "Good API development experience",
                "Cloud deployment knowledge"
            ],
            "concerns": [
                "Limited Kubernetes experience"
            ],
            "interview_recommendations": [
                "Focus on system design",
                "Ask about scalability challenges"
            ],
            "confidence_score": 88
        },
        "skills_extraction": [
            "Python", "FastAPI", "JavaScript", "React", 
            "PostgreSQL", "Docker", "AWS", "Machine Learning"
        ]
    }
    
    # Test file configurations
    TEST_FILES = {
        "valid_resume": "test_resume.pdf",
        "invalid_file": "malware.exe",
        "large_file": "huge_resume.pdf"
    }