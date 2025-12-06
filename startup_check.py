#!/usr/bin/env python3
"""
Startup validation script for Agentic HR Assistant
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'pydantic_settings',
        'sqlalchemy', 'asyncpg', 'alembic', 'anthropic',
        'passlib', 'cryptography', 'minio', 'redis', 'httpx'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package}")
            missing.append(package)
    
    return missing

def check_environment():
    """Check environment variables"""
    print("\nChecking environment configuration...")
    
    required_env_vars = [
        'DATABASE_URL', 'SECRET_KEY', 'ENCRYPTION_KEY',
        'MINIO_ENDPOINT', 'MINIO_ACCESS_KEY', 'MINIO_SECRET_KEY'
    ]
    
    # Load .env file if exists
    from dotenv import load_dotenv
    load_dotenv()
    
    missing = []
    for var in required_env_vars:
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            print(f"  ✗ {var} (missing or placeholder)")
            missing.append(var)
        else:
            print(f"  ✓ {var}")
    
    return missing

def check_imports():
    """Check if application modules import correctly"""
    print("\nChecking application imports...")
    
    try:
        from src.core.config import settings
        print("  ✓ Core configuration")
    except Exception as e:
        print(f"  ✗ Core configuration: {e}")
        return False
    
    try:
        from src.core.security import security_utils
        print("  ✓ Security utilities")
    except Exception as e:
        print(f"  ✗ Security utilities: {e}")
        return False
    
    try:
        from src.models.user import User
        from src.models.candidate import Candidate
        from src.models.job import Job
        from src.models.application import Application
        print("  ✓ Database models")
    except Exception as e:
        print(f"  ✗ Database models: {e}")
        return False
    
    try:
        from src.main import app
        print("  ✓ FastAPI application")
    except Exception as e:
        print(f"  ✗ FastAPI application: {e}")
        return False
    
    return True

def check_database_schema():
    """Check database schema files"""
    print("\nChecking database schema...")
    
    schema_files = [
        "migrations/env.py",
        "migrations/versions/001_initial_schema.py",
        "alembic.ini"
    ]
    
    missing = []
    for file_path in schema_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path}")
            missing.append(file_path)
    
    return missing

def main():
    """Main validation function"""
    print("=== Agentic HR Assistant Startup Validation ===\n")
    
    issues = []
    
    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        issues.append(f"Missing dependencies: {', '.join(missing_deps)}")
    
    # Check environment
    missing_env = check_environment()
    if missing_env:
        issues.append(f"Missing/placeholder environment variables: {', '.join(missing_env)}")
    
    # Check imports
    if not check_imports():
        issues.append("Application import errors")
    
    # Check database schema
    missing_schema = check_database_schema()
    if missing_schema:
        issues.append(f"Missing schema files: {', '.join(missing_schema)}")
    
    print("\n=== Summary ===")
    if not issues:
        print("✓ All checks passed! Application is ready to run.")
        print("\nTo start the application:")
        print("  python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("✗ Issues found:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        print("\nRecommendations:")
        if missing_deps:
            print("  - Install missing packages: pip install " + " ".join(missing_deps))
        if missing_env:
            print("  - Configure environment variables in .env file")
        if missing_schema:
            print("  - Run database migrations: alembic upgrade head")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)