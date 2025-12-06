"""
Quick test runner for HR Assistant system
"""
import asyncio
import aiohttp
import json
import time
from pathlib import Path
import sys

class HRAssistantTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_health_check(self):
        """Test basic health check endpoint"""
        print("🔍 Testing health check...")
        try:
            async with self.session.get(f"{self.base_url}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Health check passed: {data['status']}")
                    return True
                else:
                    print(f"❌ Health check failed: {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    async def test_api_docs(self):
        """Test API documentation availability"""
        print("📚 Testing API documentation...")
        try:
            async with self.session.get(f"{self.base_url}/docs") as resp:
                if resp.status == 200:
                    print("✅ API documentation is accessible")
                    return True
                else:
                    print(f"❌ API docs failed: {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ API docs error: {e}")
            return False
    
    async def test_candidate_endpoint_unauthorized(self):
        """Test that candidate endpoint requires authentication"""
        print("🔐 Testing authentication requirement...")
        try:
            async with self.session.get(f"{self.base_url}/api/v1/candidates/") as resp:
                if resp.status == 401:
                    print("✅ Authentication properly required")
                    return True
                else:
                    print(f"❌ Authentication test failed: {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ Authentication test error: {e}")
            return False
    
    async def test_cors_headers(self):
        """Test CORS headers are present"""
        print("🌐 Testing CORS configuration...")
        try:
            headers = {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Authorization'
            }
            async with self.session.options(f"{self.base_url}/api/v1/candidates/", headers=headers) as resp:
                cors_header = resp.headers.get('Access-Control-Allow-Origin')
                if cors_header:
                    print(f"✅ CORS configured: {cors_header}")
                    return True
                else:
                    print("⚠️  CORS headers not found")
                    return False
        except Exception as e:
            print(f"❌ CORS test error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all basic tests"""
        print("🚀 Starting HR Assistant system tests...\n")
        
        tests = [
            self.test_health_check,
            self.test_api_docs,
            self.test_candidate_endpoint_unauthorized,
            self.test_cors_headers
        ]
        
        results = []
        for test in tests:
            result = await test()
            results.append(result)
            print()  # Add spacing between tests
        
        passed = sum(results)
        total = len(results)
        
        print("="*50)
        print(f"Test Results: {passed}/{total} passed")
        
        if passed == total:
            print("🎉 All basic tests passed! System is ready.")
        else:
            print("⚠️  Some tests failed. Check the logs above.")
        
        return passed == total


def check_docker_services():
    """Check if Docker services are running"""
    import subprocess
    
    print("🐳 Checking Docker services...")
    try:
        result = subprocess.run(
            ["docker-compose", "ps"], 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent
        )
        
        if "hr_api" in result.stdout and "Up" in result.stdout:
            print("✅ Docker services are running")
            return True
        else:
            print("❌ Docker services not running. Please run: docker-compose up -d")
            return False
    except Exception as e:
        print(f"❌ Error checking Docker: {e}")
        return False


def create_test_data():
    """Create test data files"""
    print("📝 Creating test data...")
    
    # Create test resume
    test_resume = """John Doe
Senior Python Developer
Email: john.doe@example.com
Phone: +1234567890

EXPERIENCE:
• 5+ years of Python development
• Expertise in FastAPI, Django, Flask
• PostgreSQL and Redis experience
• AWS cloud deployment
• Team leadership and mentoring

SKILLS:
• Python, JavaScript, TypeScript
• FastAPI, React, Vue.js  
• PostgreSQL, MongoDB, Redis
• Docker, Kubernetes, AWS
• Machine Learning, Data Science

EDUCATION:
• B.S. Computer Science, MIT (2018)
• AWS Certified Solutions Architect
"""
    
    test_file = Path(__file__).parent / "test_resume.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_resume)
    
    print(f"✅ Created test resume: {test_file}")
    return test_file


async def main():
    """Main test runner"""
    print("🔧 HR Assistant - Quick System Test")
    print("="*50)
    
    # Check prerequisites
    if not check_docker_services():
        print("\n❌ Please start Docker services first:")
        print("   docker-compose up -d")
        sys.exit(1)
    
    # Create test data
    create_test_data()
    
    # Wait a moment for services to be ready
    print("⏳ Waiting for services to be ready...")
    await asyncio.sleep(3)
    
    # Run tests
    async with HRAssistantTester() as tester:
        success = await tester.run_all_tests()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Open API docs: http://localhost:8000/docs")
        print("2. Access MinIO console: http://localhost:9001")
        print("3. Run full test suite: pytest tests/ -v")
        print("4. Create your first user and start using the API!")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Check Docker logs: docker-compose logs")
        print("2. Verify .env configuration")
        print("3. Ensure all services are healthy")
        print("4. Check the TESTING_GUIDE.md for detailed help")


if __name__ == "__main__":
    asyncio.run(main())