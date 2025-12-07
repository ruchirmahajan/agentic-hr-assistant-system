"""
Test script for Ollama integration
Run with: python test_ollama.py
"""
import asyncio
import sys
sys.path.insert(0, '.')

async def test_ollama():
    """Test Ollama integration"""
    print("=" * 60)
    print("🦙 Ollama Integration Test")
    print("=" * 60)
    
    # Test 1: Check Ollama availability
    print("\n📡 Test 1: Checking Ollama availability...")
    try:
        from src.services.ollama_service import ollama_service
        
        is_available = await ollama_service.check_availability()
        if is_available:
            print("   ✅ Ollama is running and available!")
        else:
            print("   ⚠️ Ollama is not available")
            print("   💡 Make sure Ollama is running: ollama serve")
            print("   💡 Download a model: ollama pull llama2")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: List models
    print("\n📋 Test 2: Listing installed models...")
    try:
        models = await ollama_service.list_models()
        if models:
            print(f"   ✅ Found {len(models)} models:")
            for model in models:
                print(f"      - {model}")
        else:
            print("   ⚠️ No models installed")
            print("   💡 Install a model: ollama pull llama2")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test AI service integration
    print("\n🤖 Test 3: Testing integrated AI service...")
    try:
        from src.services.claude_service_free import claude_service
        
        status = await claude_service.get_ai_status()
        print(f"   Provider: {status['provider']}")
        print(f"   Ollama enabled: {status['ollama']['enabled']}")
        print(f"   Ollama available: {status['ollama']['available']}")
        print(f"   Status: {status['status']}")
        
        if status['ollama']['installed_models']:
            print(f"   Models: {status['ollama']['installed_models']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Test resume analysis
    print("\n📄 Test 4: Testing resume analysis...")
    try:
        sample_resume = """
        John Doe
        Software Engineer with 5 years of experience
        
        Skills: Python, JavaScript, FastAPI, React, PostgreSQL, Docker
        
        Experience:
        - Senior Developer at Tech Corp (2020-2023)
          Built microservices with FastAPI and Python
        - Developer at StartupXYZ (2018-2020)
          Full-stack development with React and Node.js
        
        Education:
        BS Computer Science, MIT, 2018
        """
        
        sample_job = "Looking for a Python developer with FastAPI experience"
        
        analysis = await claude_service.analyze_resume(sample_resume, sample_job)
        
        print(f"   Method used: {analysis.get('method', 'unknown')}")
        print(f"   Match score: {analysis.get('overall_match_score', 0)}")
        
        skills = analysis.get('technical_skills', {})
        if isinstance(skills, dict):
            all_skills = []
            for k, v in skills.items():
                if isinstance(v, list):
                    all_skills.extend(v)
            print(f"   Skills found: {all_skills[:10]}")
        
        print("   ✅ Resume analysis complete!")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 5: Test interview question generation
    print("\n❓ Test 5: Testing interview question generation...")
    try:
        questions = await claude_service.generate_interview_questions(
            candidate_profile={
                "skills": ["python", "fastapi", "react"],
                "experience_level": "senior"
            },
            job_description="Senior Python Developer",
            question_count=5
        )
        
        print(f"   Generated {len(questions)} questions:")
        for i, q in enumerate(questions[:5], 1):
            print(f"   {i}. {q[:80]}...")
        
        print("   ✅ Question generation complete!")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test complete!")
    print("=" * 60)
    
    # Summary
    print("\n📊 Summary:")
    if is_available and models:
        print("   🦙 Ollama is configured and ready!")
        print("   🎯 The app will use Ollama for AI analysis")
    else:
        print("   📋 Using rule-based fallback (still works!)")
        print("\n   To enable Ollama:")
        print("   1. Start Ollama: ollama serve")
        print("   2. Install a model: ollama pull llama2")
        print("   3. Run this test again")


if __name__ == "__main__":
    asyncio.run(test_ollama())
