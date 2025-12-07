"""
Ollama AI Service - Free local LLM integration for HR Assistant
Supports various models like Llama2, Mistral, CodeLlama, etc.
"""
import asyncio
import json
import logging
import httpx
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from ..core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class OllamaResponse:
    """Structured response from Ollama"""
    content: str
    model: str
    total_duration: Optional[int] = None
    eval_count: Optional[int] = None


class OllamaService:
    """
    Ollama AI Service for local LLM inference.
    
    Ollama runs locally on your machine, providing:
    - 🆓 100% FREE - No API costs ever
    - 🔒 Privacy - All data stays local
    - ⚡ Fast inference with GPU acceleration
    - 🎯 Multiple model support (Llama2, Mistral, etc.)
    """
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        self._available = None
        logger.info(f"🦙 Ollama Service initialized - Model: {self.model}")
    
    async def check_availability(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    self._available = True
                    logger.info("✅ Ollama is available and running")
                    return True
        except Exception as e:
            logger.warning(f"⚠️ Ollama not available: {e}")
        
        self._available = False
        return False
    
    async def list_models(self) -> List[str]:
        """List available models in Ollama"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    logger.info(f"📋 Available Ollama models: {models}")
                    return models
        except Exception as e:
            logger.error(f"Error listing models: {e}")
        return []
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> OllamaResponse:
        """
        Generate text using Ollama.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions
            temperature: Creativity level (0.0-1.0)
            max_tokens: Maximum response length
            
        Returns:
            OllamaResponse with generated content
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return OllamaResponse(
                        content=data.get("response", ""),
                        model=data.get("model", self.model),
                        total_duration=data.get("total_duration"),
                        eval_count=data.get("eval_count")
                    )
                else:
                    logger.error(f"Ollama error: {response.status_code} - {response.text}")
                    return OllamaResponse(content="", model=self.model)
                    
        except httpx.TimeoutException:
            logger.error(f"Ollama request timed out after {self.timeout}s")
            return OllamaResponse(content="", model=self.model)
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return OllamaResponse(content="", model=self.model)
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> OllamaResponse:
        """
        Chat completion using Ollama.
        
        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            temperature: Creativity level
            max_tokens: Maximum response length
            
        Returns:
            OllamaResponse with generated content
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    message = data.get("message", {})
                    return OllamaResponse(
                        content=message.get("content", ""),
                        model=data.get("model", self.model),
                        total_duration=data.get("total_duration"),
                        eval_count=data.get("eval_count")
                    )
                else:
                    logger.error(f"Ollama chat error: {response.status_code}")
                    return OllamaResponse(content="", model=self.model)
                    
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            return OllamaResponse(content="", model=self.model)
    
    async def analyze_resume(
        self,
        resume_text: str,
        job_description: str = "",
        position_title: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze a resume using Ollama LLM.
        
        Returns structured analysis with skills, experience, and recommendations.
        """
        system_prompt = """You are an expert HR assistant analyzing resumes.
Provide analysis in JSON format with these exact keys:
- skills: array of technical and soft skills found
- experience_years: estimated years of experience (number or null)
- skill_match_percentage: 0-100 match score against job requirements
- matched_skills: array of skills matching job requirements
- summary: 2-3 sentence summary of the candidate
- strengths: array of candidate strengths
- concerns: array of potential concerns or gaps
- recommendations: array of hiring recommendations
- interview_questions: array of 5 relevant interview questions

Be thorough but concise. Return ONLY valid JSON."""

        prompt = f"""Analyze this resume:

{resume_text[:3000]}  # Limit text length for model context

{"Job Description: " + job_description[:1000] if job_description else ""}
{"Position: " + position_title if position_title else ""}

Provide a detailed analysis in JSON format."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temperature for more consistent output
            max_tokens=2048
        )
        
        # Parse JSON response
        try:
            # Try to extract JSON from response
            content = response.content.strip()
            
            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(content)
            return analysis
            
        except json.JSONDecodeError:
            logger.warning("Could not parse Ollama response as JSON, using fallback")
            return self._extract_basic_analysis(response.content, resume_text)
    
    def _extract_basic_analysis(self, llm_response: str, resume_text: str) -> Dict[str, Any]:
        """Fallback analysis when JSON parsing fails"""
        # Basic keyword extraction
        common_skills = [
            'python', 'javascript', 'java', 'sql', 'react', 'node', 
            'aws', 'docker', 'kubernetes', 'git', 'agile', 'scrum'
        ]
        
        text_lower = resume_text.lower()
        found_skills = [s for s in common_skills if s in text_lower]
        
        return {
            "skills": found_skills,
            "experience_years": None,
            "skill_match_percentage": len(found_skills) * 10,
            "matched_skills": found_skills,
            "summary": llm_response[:500] if llm_response else "Analysis completed",
            "strengths": ["Skills identified from resume"],
            "concerns": ["Full LLM analysis incomplete - manual review recommended"],
            "recommendations": ["Review candidate details manually"],
            "interview_questions": [
                "Tell us about your background and experience.",
                "What interests you about this position?",
                "Describe a challenging project you've worked on.",
                "How do you handle tight deadlines?",
                "Where do you see yourself in 5 years?"
            ]
        }
    
    async def generate_interview_questions(
        self,
        job_title: str,
        skills: List[str],
        experience_level: str = "mid"
    ) -> List[str]:
        """Generate tailored interview questions using Ollama"""
        system_prompt = """You are an expert HR interviewer.
Generate thoughtful, role-specific interview questions.
Return a JSON array of exactly 10 questions."""

        prompt = f"""Generate interview questions for:
Position: {job_title}
Key Skills Required: {', '.join(skills)}
Experience Level: {experience_level}

Include a mix of:
- Technical questions about the required skills
- Behavioral questions
- Situational questions
- Culture fit questions

Return as JSON array of 10 questions."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1024
        )
        
        try:
            content = response.content.strip()
            if "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                if content.startswith("json"):
                    content = content[4:].strip()
            
            questions = json.loads(content)
            if isinstance(questions, list):
                return questions[:10]
        except:
            pass
        
        # Fallback questions
        return [
            f"What experience do you have with {skills[0] if skills else 'this role'}?",
            "Can you describe your most challenging project?",
            "How do you handle conflicting priorities?",
            "Describe your ideal work environment.",
            "What motivates you in your work?",
            "How do you stay updated with industry trends?",
            "Tell us about a time you had to learn something quickly.",
            "How do you approach problem-solving?",
            "What's your experience with team collaboration?",
            "Where do you see yourself growing in this role?"
        ]
    
    async def summarize_candidate(
        self,
        resume_text: str,
        job_title: str = ""
    ) -> str:
        """Generate a brief candidate summary using Ollama"""
        prompt = f"""Summarize this candidate in 3-4 sentences for a {job_title or 'general'} position:

{resume_text[:2000]}

Focus on: key skills, experience level, and fit for the role."""

        response = await self.generate(
            prompt=prompt,
            system_prompt="You are a concise HR assistant. Provide brief, professional summaries.",
            temperature=0.5,
            max_tokens=300
        )
        
        return response.content or "Unable to generate summary."
    
    async def score_candidate(
        self,
        resume_text: str,
        job_requirements: str,
        weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """Score a candidate against job requirements"""
        default_weights = {
            "skills": 0.4,
            "experience": 0.3,
            "education": 0.15,
            "culture_fit": 0.15
        }
        weights = weights or default_weights
        
        system_prompt = """You are an expert HR analyst.
Score candidates objectively based on job requirements.
Return JSON with scores from 0-100 for each category."""

        prompt = f"""Score this candidate against the job requirements:

RESUME:
{resume_text[:2500]}

JOB REQUIREMENTS:
{job_requirements[:1500]}

Provide scores (0-100) for:
- skills_score: Technical skills match
- experience_score: Experience level match  
- education_score: Education requirements match
- culture_fit_score: Potential culture fit (based on resume cues)
- overall_score: Weighted average

Return as JSON with these exact keys."""

        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=512
        )
        
        try:
            content = response.content.strip()
            if "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                if content.startswith("json"):
                    content = content[4:].strip()
            
            scores = json.loads(content)
            return scores
        except:
            # Return default scores
            return {
                "skills_score": 50,
                "experience_score": 50,
                "education_score": 50,
                "culture_fit_score": 50,
                "overall_score": 50,
                "note": "Auto-scored due to parsing error"
            }


# Singleton instance
ollama_service = OllamaService()
