# 🤖 AI Service Integration Guide

<div align="center">

![AI](https://img.shields.io/badge/AI-Rule--Based-green.svg)
![Cost](https://img.shields.io/badge/Cost-$0%20Free-brightgreen.svg)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)

**Complete guide to utilizing the Free Rule-based AI Service in the HR Assistant**

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [AI Service Options](#-ai-service-options)
- [Free Rule-Based AI](#-free-rule-based-ai)
- [Step-by-Step Integration](#-step-by-step-integration)
- [API Usage Examples](#-api-usage-examples)
- [Customization Guide](#-customization-guide)
- [Advanced Features](#-advanced-features)
- [Upgrading to Paid AI](#-upgrading-to-paid-ai)

---

## 🎯 Overview

The HR Assistant supports multiple AI providers for candidate analysis and resume scoring:

| Provider | Cost | Features | Setup Difficulty |
|----------|------|----------|------------------|
| **Rule-Based** | 🆓 Free | Basic skill matching, keyword extraction | ⭐ Easy |
| **Ollama** | 🆓 Free | Advanced analysis, local LLM | ⭐⭐ Medium |
| **Anthropic Claude** | 💰 Paid | Best accuracy, advanced reasoning | ⭐⭐ Medium |
| **OpenAI** | 💰 Paid | High quality, fast responses | ⭐⭐ Medium |

This guide focuses on the **Free Rule-Based AI** which requires **NO API keys** and **NO external services**.

---

## 🆓 AI Service Options

### Option 1: Free Rule-Based AI (Recommended for Demo)

**Location:** `src/services/free_ai_service.py`

**Features:**
- ✅ Skill extraction from resumes
- ✅ Experience years detection
- ✅ Job requirement matching
- ✅ Score calculation
- ✅ Interview question generation
- ✅ Recommendations

**Limitations:**
- No semantic understanding
- Keyword-based matching only
- Limited to predefined skills

### Option 2: Ollama (Free Local LLM)

**Location:** `src/services/opensource_ai_service.py`

**Features:**
- ✅ More intelligent analysis
- ✅ Natural language understanding
- ✅ Context-aware responses

**Requirements:**
- Install Ollama locally
- Download LLM model (llama2, mistral, etc.)

### Option 3: Claude/OpenAI (Paid)

**Location:** `src/services/claude_service.py`

**Features:**
- ✅ Best accuracy
- ✅ Advanced reasoning
- ✅ Complex analysis

**Requirements:**
- API key
- Monthly costs

---

## 🔧 Free Rule-Based AI

### How It Works

The Free AI Service uses **pattern matching** and **keyword extraction** to analyze resumes:

```
Resume Text → Skill Extraction → Experience Detection → Score Calculation → Recommendations
```

### Core Components

#### 1. Skill Keywords Dictionary
```python
skills_keywords = {
    'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy'],
    'javascript': ['javascript', 'js', 'node', 'react', 'vue', 'angular'],
    'java': ['java', 'spring', 'hibernate', 'maven', 'gradle'],
    'sql': ['sql', 'mysql', 'postgresql', 'mongodb', 'database'],
    'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
    'management': ['project management', 'team lead', 'scrum', 'agile'],
}
```

#### 2. Experience Patterns (Regex)
```python
experience_patterns = [
    r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?experience',
    r'(\d+)\+?\s*(?:years?|yrs?)',
    r'(\d+)\s*to\s*(\d+)\s*(?:years?|yrs?)',
]
```

#### 3. Scoring Algorithm
```
Score = (Matched Skills / Required Skills) × 100
```

---

## 📝 Step-by-Step Integration

### Step 1: Import the Service

```python
# In your API file (e.g., src/api/demo.py)
from src.services.free_ai_service import free_ai_service
```

### Step 2: Add AI Analysis Endpoint

Add this endpoint to `src/api/demo.py`:

```python
@demo_router.post("/candidates/{candidate_id}/analyze")
async def analyze_candidate_ai(
    candidate_id: str,
    job_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze a candidate using the Free AI Service.
    Extracts skills, calculates match score, and provides recommendations.
    """
    try:
        # Get candidate
        result = await db.execute(
            select(Candidate).where(Candidate.id == candidate_id)
        )
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Build resume text from candidate data
        resume_text = f"""
        Name: {candidate.first_name} {candidate.last_name}
        Skills: {candidate.skills or ''}
        Experience: {candidate.experience_years or 0} years
        Education: {candidate.education or ''}
        """
        
        # Get job requirements if job_id provided
        job_requirements = ""
        if job_id:
            job_result = await db.execute(
                select(Job).where(Job.id == job_id)
            )
            job = job_result.scalar_one_or_none()
            if job:
                job_requirements = f"{job.requirements or ''} {job.description or ''}"
        
        # Analyze using Free AI Service
        analysis = free_ai_service.analyze_candidate(resume_text, job_requirements)
        
        # Update candidate score in database
        candidate.ai_score = analysis.get("skill_match_percentage", 0)
        await db.commit()
        
        return {
            "candidate_id": candidate_id,
            "analysis": analysis,
            "score": analysis.get("skill_match_percentage", 0),
            "skills_found": analysis.get("skills", []),
            "matched_skills": analysis.get("matched_skills", []),
            "experience_years": analysis.get("experience_years"),
            "summary": analysis.get("summary", ""),
            "recommendations": analysis.get("recommendations", [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing candidate: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 3: Add Interview Questions Endpoint

```python
@demo_router.get("/jobs/{job_id}/interview-questions")
async def generate_interview_questions(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate interview questions based on job requirements.
    Uses the Free AI Service to create relevant questions.
    """
    try:
        # Get job
        result = await db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Extract skills from job requirements
        job_text = f"{job.title} {job.requirements or ''} {job.description or ''}"
        skills = free_ai_service.extract_skills(job_text)
        
        # Generate questions
        questions = free_ai_service.generate_interview_questions(
            job.title,
            skills
        )
        
        return {
            "job_id": job_id,
            "job_title": job.title,
            "skills_identified": skills,
            "questions": questions,
            "total_questions": len(questions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 4: Add Bulk Analysis Endpoint

```python
@demo_router.post("/jobs/{job_id}/rank-candidates")
async def rank_candidates_for_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Rank all candidates for a specific job based on skill match.
    Uses the Free AI Service to calculate scores.
    """
    try:
        # Get job
        job_result = await db.execute(
            select(Job).where(Job.id == job_id)
        )
        job = job_result.scalar_one_or_none()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job_requirements = f"{job.requirements or ''} {job.description or ''}"
        
        # Get all candidates
        candidates_result = await db.execute(select(Candidate))
        candidates = candidates_result.scalars().all()
        
        # Analyze and rank each candidate
        ranked_candidates = []
        for candidate in candidates:
            resume_text = f"""
            Skills: {candidate.skills or ''}
            Experience: {candidate.experience_years or 0} years
            Education: {candidate.education or ''}
            """
            
            analysis = free_ai_service.analyze_candidate(resume_text, job_requirements)
            
            ranked_candidates.append({
                "candidate_id": str(candidate.id),
                "name": f"{candidate.first_name} {candidate.last_name}",
                "email": candidate.email,
                "score": analysis.get("skill_match_percentage", 0),
                "matched_skills": analysis.get("matched_skills", []),
                "experience_years": candidate.experience_years,
                "recommendation": analysis.get("recommendations", [])[0] if analysis.get("recommendations") else ""
            })
        
        # Sort by score (highest first)
        ranked_candidates.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "job_id": job_id,
            "job_title": job.title,
            "total_candidates": len(ranked_candidates),
            "ranked_candidates": ranked_candidates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ranking candidates: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 5: Add to Dashboard (JavaScript)

Add these functions to `dashboard.js`:

```javascript
// Analyze a candidate using AI
async function analyzeCandidate(candidateId, jobId = null) {
    try {
        showNotification('Analyzing candidate...', 'info');
        
        let url = `${API_BASE}/candidates/${candidateId}/analyze`;
        if (jobId) {
            url += `?job_id=${jobId}`;
        }
        
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) throw new Error('Analysis failed');
        
        const data = await response.json();
        
        // Show results in modal
        showAnalysisResults(data);
        
        showNotification('Analysis complete!', 'success');
        return data;
        
    } catch (error) {
        console.error('Error analyzing candidate:', error);
        showNotification('Analysis failed', 'error');
    }
}

// Show analysis results in a modal
function showAnalysisResults(data) {
    const content = `
        <div class="space-y-4">
            <div class="bg-blue-50 p-4 rounded-lg">
                <h4 class="font-bold text-blue-800">Match Score</h4>
                <p class="text-3xl font-bold text-blue-600">${data.score.toFixed(1)}%</p>
            </div>
            
            <div class="bg-green-50 p-4 rounded-lg">
                <h4 class="font-bold text-green-800">Skills Found</h4>
                <div class="flex flex-wrap gap-2 mt-2">
                    ${data.skills_found.map(skill => 
                        `<span class="px-2 py-1 bg-green-200 text-green-800 rounded text-sm">${skill}</span>`
                    ).join('')}
                </div>
            </div>
            
            <div class="bg-purple-50 p-4 rounded-lg">
                <h4 class="font-bold text-purple-800">Matched Skills</h4>
                <div class="flex flex-wrap gap-2 mt-2">
                    ${data.matched_skills.map(skill => 
                        `<span class="px-2 py-1 bg-purple-200 text-purple-800 rounded text-sm">${skill}</span>`
                    ).join('')}
                </div>
            </div>
            
            <div class="bg-gray-50 p-4 rounded-lg">
                <h4 class="font-bold text-gray-800">Summary</h4>
                <p class="text-gray-600 mt-2">${data.summary}</p>
            </div>
            
            <div class="bg-yellow-50 p-4 rounded-lg">
                <h4 class="font-bold text-yellow-800">Recommendations</h4>
                <ul class="list-disc list-inside mt-2">
                    ${data.recommendations.map(rec => 
                        `<li class="text-yellow-700">${rec}</li>`
                    ).join('')}
                </ul>
            </div>
        </div>
    `;
    
    document.getElementById('analysis-results-content').innerHTML = content;
    document.getElementById('analysis-modal').classList.remove('hidden');
    document.getElementById('analysis-modal').classList.add('flex');
}

// Generate interview questions
async function generateInterviewQuestions(jobId) {
    try {
        showNotification('Generating questions...', 'info');
        
        const response = await fetch(`${API_BASE}/jobs/${jobId}/interview-questions`);
        
        if (!response.ok) throw new Error('Failed to generate questions');
        
        const data = await response.json();
        
        // Show questions in modal
        showInterviewQuestions(data);
        
        showNotification('Questions generated!', 'success');
        return data;
        
    } catch (error) {
        console.error('Error generating questions:', error);
        showNotification('Failed to generate questions', 'error');
    }
}

// Rank candidates for a job
async function rankCandidates(jobId) {
    try {
        showNotification('Ranking candidates...', 'info');
        
        const response = await fetch(`${API_BASE}/jobs/${jobId}/rank-candidates`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) throw new Error('Ranking failed');
        
        const data = await response.json();
        
        // Show ranked list
        showRankedCandidates(data);
        
        showNotification('Candidates ranked!', 'success');
        return data;
        
    } catch (error) {
        console.error('Error ranking candidates:', error);
        showNotification('Ranking failed', 'error');
    }
}

// Export to window for onclick handlers
window.analyzeCandidate = analyzeCandidate;
window.generateInterviewQuestions = generateInterviewQuestions;
window.rankCandidates = rankCandidates;
```

---

## 🔌 API Usage Examples

### Example 1: Analyze a Candidate

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/demo/candidates/abc123/analyze?job_id=job456"
```

**Response:**
```json
{
    "candidate_id": "abc123",
    "analysis": {
        "skills": ["python", "fastapi", "postgresql", "docker"],
        "experience_years": 5,
        "skill_match_percentage": 75.0,
        "matched_skills": ["python", "fastapi", "postgresql"],
        "summary": "Candidate has 5 years of experience. Skills include: python, fastapi, postgresql, docker. Strong match for the position.",
        "recommendations": ["Good candidate - consider for interview", "Solid skill alignment"]
    },
    "score": 75.0,
    "skills_found": ["python", "fastapi", "postgresql", "docker"],
    "matched_skills": ["python", "fastapi", "postgresql"],
    "experience_years": 5,
    "summary": "Candidate has 5 years of experience...",
    "recommendations": ["Good candidate - consider for interview"]
}
```

### Example 2: Generate Interview Questions

**Request:**
```bash
curl "http://127.0.0.1:8000/api/v1/demo/jobs/job456/interview-questions"
```

**Response:**
```json
{
    "job_id": "job456",
    "job_title": "Senior Python Developer",
    "skills_identified": ["python", "fastapi", "postgresql"],
    "questions": [
        "Can you tell us about yourself and your background?",
        "What interests you about this position?",
        "Describe your experience with teamwork.",
        "How do you handle challenging situations?",
        "Can you describe a project where you used python?",
        "How do you approach database design and optimization?"
    ],
    "total_questions": 6
}
```

### Example 3: Rank All Candidates

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/demo/jobs/job456/rank-candidates"
```

**Response:**
```json
{
    "job_id": "job456",
    "job_title": "Senior Python Developer",
    "total_candidates": 5,
    "ranked_candidates": [
        {
            "candidate_id": "c1",
            "name": "John Doe",
            "email": "john@example.com",
            "score": 85.0,
            "matched_skills": ["python", "fastapi", "docker"],
            "experience_years": 5,
            "recommendation": "Excellent candidate - recommend interview"
        },
        {
            "candidate_id": "c2",
            "name": "Jane Smith",
            "email": "jane@example.com",
            "score": 65.0,
            "matched_skills": ["python", "sql"],
            "experience_years": 3,
            "recommendation": "Good candidate - consider for interview"
        }
    ]
}
```

---

## ⚙️ Customization Guide

### Adding New Skills

Edit `src/services/free_ai_service.py`:

```python
skills_keywords = {
    # Existing categories...
    
    # Add new categories
    'devops': ['devops', 'ci/cd', 'jenkins', 'gitlab', 'terraform', 'ansible'],
    'mobile': ['android', 'ios', 'swift', 'kotlin', 'flutter', 'react native'],
    'data_science': ['machine learning', 'ml', 'deep learning', 'tensorflow', 'pytorch'],
    'frontend': ['html', 'css', 'sass', 'webpack', 'tailwind'],
    'backend': ['api', 'rest', 'graphql', 'microservices'],
}
```

### Adding New Experience Patterns

```python
experience_patterns = [
    # Existing patterns...
    
    # Add new patterns
    r'worked\s*for\s*(\d+)\s*(?:years?|yrs?)',
    r'(\d+)\s*(?:years?|yrs?)\s*in\s*industry',
    r'since\s*(\d{4})',  # Calculate from year
]
```

### Custom Scoring Algorithm

```python
def calculate_score(self, candidate_skills, required_skills, experience_years):
    """Custom scoring with weighted factors"""
    
    # Skill match (60% weight)
    if required_skills:
        skill_score = len(set(candidate_skills) & set(required_skills)) / len(required_skills) * 60
    else:
        skill_score = 30  # Base score if no requirements
    
    # Experience bonus (30% weight)
    if experience_years:
        experience_score = min(experience_years * 3, 30)  # Max 30 points
    else:
        experience_score = 0
    
    # Education bonus (10% weight) - implement as needed
    education_score = 10  # Placeholder
    
    return skill_score + experience_score + education_score
```

### Custom Interview Questions

```python
def generate_interview_questions(self, job_title: str, skills: List[str]) -> List[str]:
    """Generate custom interview questions"""
    
    questions = []
    
    # Role-specific questions
    if 'senior' in job_title.lower():
        questions.extend([
            "Describe a time you mentored junior developers.",
            "How do you approach technical decision-making?",
            "What's your experience with system architecture?"
        ])
    
    # Technical questions by skill
    skill_questions = {
        'python': [
            "Explain Python's GIL and its implications.",
            "What are decorators and when would you use them?",
            "How do you handle memory management in Python?"
        ],
        'fastapi': [
            "What advantages does FastAPI have over Flask?",
            "How do you handle authentication in FastAPI?",
            "Explain dependency injection in FastAPI."
        ],
        'sql': [
            "Explain the difference between INNER and OUTER joins.",
            "How do you optimize slow queries?",
            "What are database indexes and when to use them?"
        ]
    }
    
    for skill in skills:
        if skill in skill_questions:
            questions.extend(skill_questions[skill][:2])  # Add 2 questions per skill
    
    return questions
```

---

## 🚀 Advanced Features

### 1. Resume Text Extraction

Add PDF/DOCX parsing:

```python
# In src/services/free_ai_service.py

import PyPDF2
from docx import Document

def extract_text_from_file(self, file_path: str) -> str:
    """Extract text from uploaded resume files"""
    
    if file_path.endswith('.pdf'):
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    
    elif file_path.endswith('.docx'):
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    
    elif file_path.endswith('.txt'):
        with open(file_path, 'r') as f:
            return f.read()
    
    return ""
```

### 2. Batch Analysis

```python
async def analyze_batch(self, candidate_ids: List[str], job_id: str) -> List[Dict]:
    """Analyze multiple candidates at once"""
    results = []
    for cid in candidate_ids:
        analysis = await self.analyze_candidate(cid, job_id)
        results.append(analysis)
    return sorted(results, key=lambda x: x['score'], reverse=True)
```

### 3. Analysis Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def analyze_candidate_cached(self, resume_hash: str, requirements_hash: str) -> Dict:
    """Cache analysis results to avoid recomputation"""
    # ... analysis logic
```

---

## 💰 Upgrading to Paid AI

When you're ready to upgrade, simply change the AI provider:

### Option 1: Use Claude API

```python
# In .env
AI_PROVIDER=claude
ANTHROPIC_API_KEY=your-api-key-here

# The application will automatically use ClaudeService
```

### Option 2: Use OpenAI

```python
# In .env
AI_PROVIDER=openai
OPENAI_API_KEY=your-api-key-here
```

### Option 3: Use Local Ollama

```bash
# Install Ollama
# Visit: https://ollama.ai/download

# Pull a model
ollama pull llama2

# In .env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

---

## 📊 Comparison: Free vs Paid

| Feature | Free Rule-Based | Ollama (Free) | Claude (Paid) |
|---------|-----------------|---------------|---------------|
| Skill Extraction | ✅ Keyword | ✅ Semantic | ✅ Semantic |
| Experience Detection | ✅ Regex | ✅ NLP | ✅ NLP |
| Summary Generation | ✅ Template | ✅ AI-generated | ✅ AI-generated |
| Accuracy | ~70% | ~85% | ~95% |
| Speed | ⚡ Fast | 🐢 Slow | ⚡ Fast |
| Cost | $0 | $0 | ~$0.01/analysis |
| Setup | Easy | Medium | Easy |
| Offline | ✅ Yes | ✅ Yes | ❌ No |

---

## 🎯 Summary

The Free Rule-Based AI Service provides:

1. **Zero Cost** - No API keys or external services needed
2. **Full Functionality** - Skill extraction, scoring, and recommendations
3. **Easy Integration** - Just import and use
4. **Customizable** - Add your own skills and patterns
5. **Upgrade Path** - Easy to switch to paid AI later

**Start with free, upgrade when needed!**

---

<div align="center">

**Built with ❤️ for budget-conscious HR teams**

</div>
