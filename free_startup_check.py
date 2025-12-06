#!/usr/bin/env python3
"""
Free Startup Check - Verify all free dependencies work
NO PAID SERVICES REQUIRED!
"""
import sys
import os
from pathlib import Path

print("🆓 === FREE HR Assistant Startup Check ===")
print("No paid APIs or services required!")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_free_dependencies():
    """Check all free dependencies"""
    print("\n🔍 Checking FREE dependencies...")
    
    required_free = [
        "fastapi", "uvicorn", "pydantic", "pydantic_settings",
        "sqlalchemy", "asyncpg", "alembic", "passlib", 
        "cryptography", "aiofiles", "python_dotenv"
    ]
    
    missing = []
    for pkg in required_free:
        try:
            __import__(pkg.replace("_", "-"))
            print(f"  ✅ {pkg}")
        except ImportError:
            missing.append(pkg)
            print(f"  ❌ {pkg} (missing)")
    
    return missing

def check_free_environment():
    """Check free environment variables"""
    print("\n🔍 Checking FREE environment configuration...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Only check essential free variables
    required_vars = {
        "DATABASE_URL": "postgresql connection string",
        "SECRET_KEY": "JWT secret key", 
        "ENCRYPTION_KEY": "data encryption key"
    }
    
    issues = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value in ["test_key_placeholder", "your_secure_password"]:
            print(f"  ❌ {var} ({description}) - needs real value")
            issues.append(var)
        else:
            print(f"  ✅ {var}")
    
    # Check optional free services
    optional_vars = {
        "STORAGE_PATH": os.getenv("STORAGE_PATH", "./storage"),
        "AI_PROVIDER": os.getenv("AI_PROVIDER", "rules"),
        "REDIS_URL": os.getenv("REDIS_URL", "not configured")
    }
    
    print("\n📁 Free storage and AI configuration:")
    for var, value in optional_vars.items():
        print(f"  ℹ️  {var}: {value}")
    
    return issues

def check_free_imports():
    """Check free application imports"""
    print("\n🔍 Checking FREE application imports...")
    
    try:
        from core.config import settings
        print("  ✅ Core configuration")
        
        from services.claude_service_free import claude_service
        print("  ✅ Free AI service (no paid APIs)")
        
        from services.free_file_service import file_service
        print("  ✅ Free file storage (local filesystem)")
        
        from services.gdpr_service import gdpr_service
        print("  ✅ GDPR service")
        
        from main import app
        print("  ✅ FastAPI application")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def check_storage_setup():
    """Check free local storage setup"""
    print("\n📁 Setting up FREE local storage...")
    
    storage_path = Path("./storage")
    uploads_path = storage_path / "uploads"
    resumes_path = storage_path / "resumes"
    docs_path = storage_path / "documents"
    
    for path in [storage_path, uploads_path, resumes_path, docs_path]:
        path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {path}")
    
    return True

def main():
    """Run complete free startup check"""
    
    print("💰 COST: $0.00 (100% FREE)")
    print("🚫 NO paid APIs required (Claude, OpenAI, etc.)")
    print("🚫 NO cloud storage costs (AWS S3, etc.)")
    print("🚫 NO expensive databases required")
    
    # Check dependencies
    missing_deps = check_free_dependencies()
    
    # Check environment
    env_issues = check_free_environment()
    
    # Setup storage
    storage_ok = check_storage_setup()
    
    # Check imports
    import_ok = check_free_imports()
    
    # Summary
    print("\n📊 === FREE SETUP SUMMARY ===")
    
    if missing_deps:
        print(f"❌ Missing FREE dependencies: {', '.join(missing_deps)}")
        print("   Install with: pip install -r requirements_free.txt")
    
    if env_issues:
        print(f"❌ Environment issues: {', '.join(env_issues)}")
        print("   Update your .env file with real values")
    
    if not import_ok:
        print("❌ Import issues found")
    
    if not missing_deps and not env_issues and import_ok and storage_ok:
        print("🎉 SUCCESS! Ready to run with 100% FREE setup!")
        print("\n🚀 To start the application:")
        print("   python -m uvicorn src.main:app --reload")
        print("\n💡 Features available for FREE:")
        print("   • Resume parsing and analysis")
        print("   • Interview question generation")
        print("   • Candidate assessment")
        print("   • File upload and storage")
        print("   • GDPR compliance")
        print("   • REST API")
        print("   • Web interface")
        return True
    else:
        print("❌ Setup incomplete. Please fix issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)