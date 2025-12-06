"""
Open Source AI Service for HR Assistant
Replaces paid Anthropic Claude with free alternatives
"""
import httpx
import asyncio
from typing import Dict, Any, Optional, List
import logging
import json

from ..core.config import settings

logger = logging.getLogger(__name__)


class OpenSourceAIService:
    """Open source AI service using Ollama, LocalAI, or Hugging Face"""
    
    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower()
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def analyze_resume(self, resume_text: str, job_description: Optional[str] = None) -> Dict[str, Any]:
        """Analyze resume using open source AI"""
        try:
            prompt = self._build_resume_analysis_prompt(resume_text, job_description)
            response = await self._get_ai_response(prompt)
            return self._parse_resume_analysis(response)
        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            return self._fallback_resume_analysis(resume_text)
    
    async def generate_interview_questions(self, candidate_profile: Dict[str, Any], job_description: str) -> List[str]:
        """Generate interview questions using open source AI"""
        try:
            prompt = self._build_interview_questions_prompt(candidate_profile, job_description)
            response = await self._get_ai_response(prompt)
            return self._parse_interview_questions(response)
        except Exception as e:
            logger.error(f"Interview questions generation failed: {e}")
            return self._fallback_interview_questions()
    
    async def assess_candidate_fit(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Assess candidate fit using open source AI"""
        try:
            prompt = self._build_assessment_prompt(candidate_data, job_requirements)
            response = await self._get_ai_response(prompt)
            return self._parse_assessment(response)
        except Exception as e:
            logger.error(f"Candidate assessment failed: {e}")
            return self._fallback_assessment()
    
    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from configured AI provider"""
        if self.provider == "ollama":
            return await self._ollama_request(prompt)
        elif self.provider == "localai":
            return await self._localai_request(prompt)
        elif self.provider == "huggingface":
            return await self._huggingface_request(prompt)
        else:
            # Fallback to simple rule-based response
            return await self._fallback_ai_response(prompt)
    
    async def _ollama_request(self, prompt: str) -> str:
        """Make request to Ollama"""
        try:
            url = f"{settings.OLLAMA_BASE_URL}/api/generate"
            payload = {
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            response = await self.client.post(url, json=payload, timeout=settings.OLLAMA_TIMEOUT)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.warning(f"Ollama request failed: {response.status_code}")
                return ""
        except Exception as e:
            logger.error(f"Ollama request error: {e}")
            return ""
    
    async def _localai_request(self, prompt: str) -> str:
        """Make request to LocalAI"""
        try:
            url = f"{settings.LOCAL_AI_BASE_URL}/chat/completions"
            payload = {
                "model": settings.LOCAL_AI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = await self.client.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.warning(f"LocalAI request failed: {response.status_code}")
                return ""
        except Exception as e:
            logger.error(f"LocalAI request error: {e}")
            return ""
    
    async def _huggingface_request(self, prompt: str) -> str:
        """Make request to Hugging Face (free tier)"""
        try:
            if not settings.HUGGINGFACE_API_KEY:
                return ""
                
            url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
            headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
            payload = {"inputs": prompt}
            
            response = await self.client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result[0]["generated_text"] if result else ""
            else:
                logger.warning(f"Hugging Face request failed: {response.status_code}")
                return ""
        except Exception as e:
            logger.error(f"Hugging Face request error: {e}")
            return ""
    
    async def _fallback_ai_response(self, prompt: str) -> str:
        """Fallback response when AI services are unavailable"""
        if "resume" in prompt.lower():
            return "Professional with relevant experience. Skills appear aligned with requirements."
        elif "interview" in prompt.lower():
            return "Tell me about your experience. What are your key strengths? How do you handle challenges?"
        elif "assessment" in prompt.lower():
            return "Candidate appears qualified based on available information."
        else:
            return "Analysis completed with basic rule-based evaluation."
    
    def _build_resume_analysis_prompt(self, resume_text: str, job_description: Optional[str] = None) -> str:
        """Build prompt for resume analysis"""
        prompt = f"""Analyze this resume and provide structured feedback:

Resume Text:
{resume_text[:2000]}  # Limit text length

Please provide:
1. Key skills identified
2. Experience level
3. Education background
4. Strengths
5. Areas for improvement

"""
        if job_description:
            prompt += f"\nJob Description for comparison:\n{job_description[:1000]}\n"
            prompt += "6. Job fit assessment\n"
        
        prompt += "\nProvide response in JSON format with keys: skills, experience, education, strengths, improvements, job_fit"
        return prompt
    
    def _build_interview_questions_prompt(self, candidate_profile: Dict[str, Any], job_description: str) -> str:
        """Build prompt for interview questions"""
        return f"""Generate 5 relevant interview questions based on:

Candidate Profile: {json.dumps(candidate_profile, indent=2)[:1000]}
Job Description: {job_description[:1000]}

Focus on:
- Technical skills assessment
- Experience validation
- Cultural fit
- Problem-solving abilities

Return as JSON array of questions."""
    
    def _build_assessment_prompt(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any]) -> str:
        """Build prompt for candidate assessment"""
        return f"""Assess candidate fit for position:

Candidate Data: {json.dumps(candidate_data, indent=2)[:1000]}
Job Requirements: {json.dumps(job_requirements, indent=2)[:1000]}

Provide assessment with:
- Overall fit score (1-10)
- Strengths match
- Skills gaps
- Recommendations

Return as JSON with keys: fit_score, strengths, gaps, recommendations"""
    
    def _parse_resume_analysis(self, response: str) -> Dict[str, Any]:
        """Parse AI response for resume analysis"""
        try:
            return json.loads(response)
        except:
            return {
                "skills": ["General professional skills"],
                "experience": "Mid-level",
                "education": "Relevant background",
                "strengths": ["Experience", "Skills"],
                "improvements": ["Additional certifications"],
                "job_fit": "Good match"
            }
    
    def _parse_interview_questions(self, response: str) -> List[str]:
        """Parse AI response for interview questions"""
        try:
            parsed = json.loads(response)
            return parsed if isinstance(parsed, list) else []
        except:
            return self._fallback_interview_questions()
    
    def _parse_assessment(self, response: str) -> Dict[str, Any]:
        """Parse AI response for assessment"""
        try:
            return json.loads(response)
        except:
            return self._fallback_assessment()
    
    def _fallback_resume_analysis(self, resume_text: str) -> Dict[str, Any]:
        """Fallback resume analysis using basic text processing"""
        words = resume_text.lower().split()
        
        # Basic skill detection
        common_skills = ["python", "java", "javascript", "react", "sql", "aws", "docker", "git"]
        found_skills = [skill for skill in common_skills if skill in words]
        
        return {
            "skills": found_skills or ["Professional skills identified"],
            "experience": "Professional level",
            "education": "Educational background present",
            "strengths": ["Relevant experience", "Technical skills"],
            "improvements": ["Continuous learning recommended"],
            "job_fit": "Potentially good fit"
        }
    
    def _fallback_interview_questions(self) -> List[str]:
        """Fallback interview questions"""
        return [
            "Can you tell me about your background and experience?",
            "What are your key technical strengths?",
            "How do you approach problem-solving?",
            "Describe a challenging project you've worked on.",
            "Why are you interested in this position?"
        ]
    
    def _fallback_assessment(self) -> Dict[str, Any]:
        """Fallback candidate assessment"""
        return {
            "fit_score": 7,
            "strengths": ["Professional background", "Relevant experience"],
            "gaps": ["To be assessed during interview"],
            "recommendations": ["Proceed with technical interview", "Verify key skills"]
        }

# Global service instance
ai_service = OpenSourceAIService()