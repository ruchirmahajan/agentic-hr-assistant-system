#!/usr/bin/env python3
"""
🆓 FREE HR Assistant MVP Startup
Start the complete HR system with $0.00 cost!
"""
import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def install_missing_deps():
    """Install any missing dependencies"""
    import subprocess
    
    required_packages = [
        "fastapi", "uvicorn", "pydantic", "pydantic-settings",
        "sqlalchemy", "aiofiles", "python-dotenv", "cryptography",
        "passlib", "python-jose", "PyPDF2", "python-docx"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def setup_directories():
    """Setup required directories"""
    dirs = ["storage", "storage/uploads", "storage/resumes", "storage/documents"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created: {dir_path}")

def check_environment():
    """Check environment setup"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["DATABASE_URL", "SECRET_KEY", "ENCRYPTION_KEY"]
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or "placeholder" in value.lower() or "your_" in value:
            missing.append(var)
    
    return missing

def main():
    """Start the FREE HR Assistant MVP"""
    print("🆓 === FREE HR Assistant MVP Startup ===")
    print("💰 Cost: $0.00 - No paid APIs required!")
    print()
    
    # Install dependencies if needed
    print("🔍 Checking dependencies...")
    install_missing_deps()
    print("✅ Dependencies ready")
    
    # Setup directories
    print("📁 Setting up storage...")
    setup_directories()
    print("✅ Storage ready")
    
    # Check environment
    print("⚙️ Checking environment...")
    missing_vars = check_environment()
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Please update your .env file with real values")
        return False
    print("✅ Environment ready")
    
    # Import and start the application
    try:
        print("🚀 Starting HR Assistant...")
        import uvicorn
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if main():
        print("🎉 HR Assistant MVP is running!")
        print("📖 Open http://localhost:8000/docs for API documentation")
        print("🔧 Open http://localhost:8000/health for health check")
    else:
        print("❌ Failed to start HR Assistant MVP")
        sys.exit(1)