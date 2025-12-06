"""
Free AI Service - Rule-based candidate analysis without external APIs
"""
import re
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FreeAIService:
    """Free rule-based AI service - no external API costs"""
    
    def __init__(self):
        self.skills_keywords = {
            'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue', 'angular'],
            'java': ['java', 'spring', 'hibernate', 'maven', 'gradle'],
            'sql': ['sql', 'mysql', 'postgresql', 'mongodb', 'database'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'management': ['project management', 'team lead', 'scrum', 'agile'],
        }
        
        self.experience_patterns = [
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\s*to\s*(\d+)\s*(?:years?|yrs?)',
        ]
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using keyword matching"""
        text = text.lower()
        found_skills = []
        
        for category, keywords in self.skills_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    found_skills.append(keyword)
        
        return list(set(found_skills))
    
    def extract_experience_years(self, text: str) -> Optional[int]:
        """Extract years of experience from text"""
        text = text.lower()
        
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if isinstance(matches[0], tuple):
                    # Range found, return average
                    try:
                        return (int(matches[0][0]) + int(matches[0][1])) // 2
                    except ValueError:
                        continue
                else:
                    # Single number
                    try:
                        return int(matches[0])
                    except ValueError:
                        continue
        
        return None
    
    def analyze_candidate(self, resume_text: str, job_requirements: str = "") -> Dict[str, Any]:
        """Analyze candidate resume using rule-based approach"""
        try:
            candidate_skills = self.extract_skills(resume_text)
            required_skills = self.extract_skills(job_requirements) if job_requirements else []
            experience_years = self.extract_experience_years(resume_text)
            
            # Calculate skill match percentage
            if required_skills:
                matched_skills = set(candidate_skills) & set(required_skills)
                skill_match_percentage = len(matched_skills) / len(required_skills) * 100
            else:
                skill_match_percentage = 0
            
            # Generate simple summary
            summary = self._generate_summary(candidate_skills, experience_years, skill_match_percentage)
            
            return {
                "skills": candidate_skills,
                "experience_years": experience_years,
                "skill_match_percentage": skill_match_percentage,
                "matched_skills": list(set(candidate_skills) & set(required_skills)),
                "summary": summary,
                "recommendations": self._generate_recommendations(skill_match_percentage)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing candidate: {e}")
            return {
                "skills": [],
                "experience_years": None,
                "skill_match_percentage": 0,
                "matched_skills": [],
                "summary": "Unable to analyze resume",
                "recommendations": ["Please review resume manually"]
            }
    
    def _generate_summary(self, skills: List[str], experience: Optional[int], match_percentage: float) -> str:
        """Generate a simple text summary"""
        parts = []
        
        if experience:
            parts.append(f"Candidate has {experience} years of experience")
        
        if skills:
            parts.append(f"Skills include: {', '.join(skills[:5])}")
        
        if match_percentage > 70:
            parts.append("Strong match for the position")
        elif match_percentage > 40:
            parts.append("Moderate match for the position")
        else:
            parts.append("May need additional evaluation")
        
        return ". ".join(parts) + "."
    
    def _generate_recommendations(self, match_percentage: float) -> List[str]:
        """Generate simple recommendations"""
        if match_percentage > 80:
            return ["Excellent candidate - recommend interview", "High skill match"]
        elif match_percentage > 60:
            return ["Good candidate - consider for interview", "Solid skill alignment"]
        elif match_percentage > 40:
            return ["Moderate fit - review carefully", "Some skill gaps identified"]
        else:
            return ["Limited match - consider other candidates", "Significant skill gaps"]
    
    def generate_interview_questions(self, job_title: str, skills: List[str]) -> List[str]:
        """Generate basic interview questions"""
        questions = [
            "Can you tell us about yourself and your background?",
            "What interests you about this position?",
            "Describe your experience with teamwork.",
            "How do you handle challenging situations?"
        ]
        
        # Add skill-specific questions
        for skill in skills[:3]:  # Top 3 skills
            if skill in ['python', 'javascript', 'java']:
                questions.append(f"Can you describe a project where you used {skill}?")
            elif skill in ['sql', 'database']:
                questions.append("How do you approach database design and optimization?")
            elif skill in ['management', 'team lead']:
                questions.append("Describe your leadership style and experience managing teams.")
        
        return questions

# Global instance
free_ai_service = FreeAIService()