#!/usr/bin/env python3
"""
🚀 FREE HR Assistant - Complete Startup
Launch your complete HR management system with modern dashboard!
"""
import sys
import os
import webbrowser
import time
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
    
    print("📦 Checking dependencies...")
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   📥 Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def setup_directories():
    """Setup required directories"""
    dirs = ["storage", "storage/uploads", "storage/resumes", "storage/documents"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("📁 Storage directories ready")

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

def open_dashboard():
    """Open the dashboard in browser"""
    time.sleep(3)  # Wait for server to start
    
    urls_to_try = [
        "http://localhost:8000/login",
        "http://localhost:8000/dashboard",
        "http://localhost:8000/docs"
    ]
    
    print("🌐 Opening dashboard in browser...")
    for url in urls_to_try:
        try:
            webbrowser.open(url)
            print(f"   🎯 Opened: {url}")
            break
        except:
            continue

def main():
    """Launch the complete HR Assistant system"""
    print("🆓 === FREE HR Assistant - Complete System ===")
    print("💰 Total Cost: $0.00 - No subscriptions, No API fees!")
    print()
    
    # Install dependencies
    install_missing_deps()
    
    # Setup directories
    setup_directories()
    
    # Check environment
    print("⚙️ Checking environment...")
    missing_vars = check_environment()
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Please update your .env file with real values")
        return False
    print("✅ Environment configured")
    
    # Start the application
    try:
        print("🚀 Starting HR Assistant with Dashboard...")
        print()
        print("🎯 Available URLs:")
        print("   📊 Dashboard:     http://localhost:8000/dashboard")
        print("   🔐 Login:         http://localhost:8000/login")
        print("   📖 API Docs:      http://localhost:8000/docs")
        print("   ❤️  Health:       http://localhost:8000/health")
        print()
        print("🔑 Demo Login Credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print()
        print("🎉 Features Available:")
        print("   ✅ Modern Web Dashboard")
        print("   ✅ Candidate Management")
        print("   ✅ Job Posting & Management")
        print("   ✅ Application Tracking")
        print("   ✅ AI-Powered Resume Analysis (FREE)")
        print("   ✅ File Upload & Storage")
        print("   ✅ GDPR Compliance")
        print("   ✅ REST API with Documentation")
        print()
        print("⚡ Auto-opening dashboard in browser...")
        
        # Schedule browser opening
        import threading
        threading.Thread(target=open_dashboard, daemon=True).start()
        
        # Start the server
        import uvicorn
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down HR Assistant...")
        print("✅ System stopped gracefully")
        return True
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)