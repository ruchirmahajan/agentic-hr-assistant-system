"""
Free AI Service for resume analysis and candidate scoring - NO API COSTS
"""
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from ..core.config import settings
from ..core.exceptions import HRAssistantException
from .free_ai_service import free_ai_service

logger = logging.getLogger(__name__)


@dataclass
class CandidateAnalysis:
    """Structured candidate analysis results"""
    overall_match_score: float
    technical_skills: Dict[str, List[str]]
    experience_analysis: Dict[str, Any]
    education_analysis: Dict[str, Any]
    strengths: List[str]
    concerns: List[str]
    interview_recommendations: List[str]
    confidence_score: float


class FreeClaudeService:
    """Free alternative to Claude service - uses rule-based analysis"""
    
    def __init__(self):
        self.ai_service = free_ai_service
        logger.info("🆓 FREE AI Service initialized - NO API COSTS!")
    
    async def analyze_resume(
        self,
        resume_text: str,
        job_description: str = "",
        position_title: str = "",
        required_skills: List[str] = None
    ) -> CandidateAnalysis:
        """Analyze resume using free rule-based approach"""
        try:
            # Use free AI service
            analysis = self.ai_service.analyze_candidate(resume_text, job_description)
            
            # Convert to expected format
            return CandidateAnalysis(
                overall_match_score=analysis["skill_match_percentage"],
                technical_skills={"identified": analysis["skills"]},
                experience_analysis={"years": analysis.get("experience_years")},
                education_analysis={"summary": "Extracted from resume"},
                strengths=analysis["matched_skills"] if analysis["matched_skills"] else ["Skills identified from resume"],
                concerns=["Manual review recommended"] if analysis["skill_match_percentage"] < 50 else [],
                interview_recommendations=self.ai_service.generate_interview_questions(
                    position_title or "General Position", 
                    analysis["skills"]
                ),
                confidence_score=85.0  # Fixed confidence for rule-based analysis
            )
            
        except Exception as e:
            logger.error(f"Error in free resume analysis: {e}")
            # Return default analysis
            return CandidateAnalysis(
                overall_match_score=0.0,
                technical_skills={"identified": []},
                experience_analysis={"years": None},
                education_analysis={"summary": "Unable to analyze"},
                strengths=["Manual review required"],
                concerns=["Analysis failed"],
                interview_recommendations=["Standard interview questions"],
                confidence_score=0.0
            )
    
    async def analyze_resume_against_job(
        self, 
        resume_text: str, 
        job_description: str,
        job_requirements: Dict[str, Any] = None
    ) -> CandidateAnalysis:
        """Analyze resume against job - free version"""
        return await self.analyze_resume(resume_text, job_description)
    
    async def extract_skills_from_resume(self, resume_text: str) -> List[str]:
        """Extract skills from resume text - free version"""
        analysis = self.ai_service.analyze_candidate(resume_text)
        return analysis["skills"]
    
    async def generate_interview_questions(
        self,
        candidate_analysis: CandidateAnalysis,
        job_title: str,
        job_requirements: Dict[str, Any] = None
    ) -> List[str]:
        """Generate interview questions based on analysis"""
        skills = candidate_analysis.technical_skills.get("identified", [])
        return self.ai_service.generate_interview_questions(job_title, skills)


# Create service instance using the free version
claude_service = FreeClaudeService()