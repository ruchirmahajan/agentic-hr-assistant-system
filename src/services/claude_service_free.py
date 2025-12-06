"""
Open Source AI Service for HR Assistant (replaces Claude)
Provides free alternatives to expensive AI services
"""
from typing import Dict, Any, List, Optional
import logging
import json
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenSourceClaudeService:
    """
    Free open source replacement for Claude AI service
    Uses rule-based processing and simple text analysis
    """
    
    def __init__(self):
        """Initialize the free service"""
        logger.info("Initialized open source HR AI service (Claude replacement)")
        self.skill_keywords = {
            "programming": ["python", "java", "javascript", "c++", "c#", "php", "ruby", "go", "rust"],
            "web": ["html", "css", "react", "angular", "vue", "node", "express", "django", "flask"],
            "database": ["sql", "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle"],
            "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible"],
            "data": ["pandas", "numpy", "sql", "excel", "tableau", "powerbi", "spark", "hadoop"],
            "management": ["team", "leadership", "project", "agile", "scrum", "management"],
            "design": ["figma", "photoshop", "illustrator", "sketch", "ui", "ux", "design"]
        }
        
        self.experience_indicators = [
            "years", "year", "experience", "worked", "developed", "led", "managed",
            "created", "built", "designed", "implemented", "delivered"
        ]
    
    async def analyze_resume(
        self, 
        resume_text: str, 
        job_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze resume using free text processing
        """
        try:
            text_lower = resume_text.lower()
            
            # Extract skills
            skills = self._extract_skills(text_lower)
            
            # Analyze experience level
            experience = self._analyze_experience(text_lower)
            
            # Extract education
            education = self._extract_education(text_lower)
            
            # Calculate job fit if job description provided
            job_fit = self._calculate_job_fit(text_lower, job_description) if job_description else 0.7
            
            analysis = {
                "overall_match_score": job_fit,
                "technical_skills": skills,
                "experience_analysis": experience,
                "education_analysis": education,
                "strengths": self._identify_strengths(skills, experience),
                "concerns": self._identify_concerns(skills, experience),
                "interview_recommendations": self._generate_interview_recommendations(skills),
                "confidence_score": 0.8,
                "analysis_date": datetime.now().isoformat(),
                "method": "open_source_text_analysis"
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            return self._fallback_analysis()
    
    async def generate_interview_questions(
        self, 
        candidate_profile: Dict[str, Any], 
        job_description: str,
        question_count: int = 5
    ) -> List[str]:
        """
        Generate interview questions using template-based approach
        """
        try:
            skills = candidate_profile.get("skills", [])
            experience = candidate_profile.get("experience_level", "mid")
            
            questions = []
            
            # Generic questions
            questions.extend([
                "Can you tell me about your background and what brings you here today?",
                "What interests you most about this position and our company?",
                "What do you consider your greatest professional achievement?"
            ])
            
            # Skill-based questions
            if isinstance(skills, dict):
                for category, skill_list in skills.items():
                    if skill_list and category in ["programming", "technical"]:
                        questions.append(f"Can you describe your experience with {', '.join(skill_list[:3])}?")
                        break
            
            # Experience-based questions
            if experience == "senior":
                questions.append("How do you approach mentoring junior team members?")
            else:
                questions.append("How do you stay current with new technologies and industry trends?")
            
            # Situational questions
            questions.extend([
                "Tell me about a challenging problem you solved recently.",
                "How do you handle tight deadlines and competing priorities?",
                "Where do you see yourself professionally in the next 3-5 years?"
            ])
            
            return questions[:question_count]
            
        except Exception as e:
            logger.error(f"Interview questions generation failed: {e}")
            return self._fallback_questions()
    
    async def assess_candidate_fit(
        self,
        candidate_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess candidate fit using rule-based matching
        """
        try:
            candidate_skills = candidate_data.get("skills", {})
            required_skills = job_requirements.get("required_skills", [])
            
            # Calculate skill match
            skill_match = self._calculate_skill_match(candidate_skills, required_skills)
            
            # Calculate experience match
            candidate_exp = candidate_data.get("experience_years", 0)
            required_exp = job_requirements.get("minimum_experience", 0)
            exp_match = min(1.0, candidate_exp / max(required_exp, 1))
            
            # Overall fit score
            fit_score = (skill_match * 0.6 + exp_match * 0.4) * 10
            
            return {
                "fit_score": round(fit_score, 1),
                "skill_match_percentage": round(skill_match * 100, 1),
                "experience_match": "adequate" if exp_match >= 0.8 else "below_requirement",
                "strengths": self._identify_match_strengths(candidate_skills, required_skills),
                "gaps": self._identify_skill_gaps(candidate_skills, required_skills),
                "recommendation": self._generate_recommendation(fit_score),
                "assessment_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Candidate assessment failed: {e}")
            return self._fallback_assessment()
    
    async def generate_job_description(
        self,
        role_title: str,
        company_info: Dict[str, Any],
        requirements: List[str],
        benefits: Optional[List[str]] = None
    ) -> str:
        """
        Generate job description using templates
        """
        try:
            company_name = company_info.get("name", "Our Company")
            company_desc = company_info.get("description", "A growing company focused on innovation")
            
            description = f"""# {role_title}

## Company Overview
{company_name} - {company_desc}

## Position Summary
We are seeking a qualified {role_title} to join our dynamic team and contribute to our continued growth and success.

## Key Responsibilities
"""
            
            # Add requirements as responsibilities
            for i, req in enumerate(requirements[:8], 1):
                description += f"{i}. {req.capitalize()}\n"
            
            description += f"""
## Requirements
• Professional experience in relevant field
• Strong communication and teamwork skills
• Ability to work independently and manage priorities
• Commitment to quality and continuous improvement
"""
            
            # Add specific requirements
            for req in requirements:
                description += f"• {req}\n"
            
            description += "\n## Benefits\n"
            if benefits:
                for benefit in benefits:
                    description += f"• {benefit}\n"
            else:
                description += """• Competitive salary
• Professional development opportunities
• Health and wellness benefits
• Flexible work environment
• Career growth potential
"""
            
            description += f"""
## How to Apply
Please submit your resume and cover letter detailing your relevant experience for the {role_title} position.

---
*Equal Opportunity Employer*
"""
            
            return description
            
        except Exception as e:
            logger.error(f"Job description generation failed: {e}")
            return f"# {role_title}\n\nPosition available. Please contact HR for details."
    
    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills from resume text"""
        found_skills = {}
        
        for category, keywords in self.skill_keywords.items():
            found = []
            for keyword in keywords:
                if keyword in text:
                    found.append(keyword.title())
            
            if found:
                found_skills[category] = found
        
        return found_skills
    
    def _analyze_experience(self, text: str) -> Dict[str, Any]:
        """Analyze experience level from text"""
        # Look for year mentions
        year_matches = re.findall(r'(\d+)\s*(?:years?|yrs?)', text)
        max_years = max([int(y) for y in year_matches], default=0)
        
        # Count experience indicators
        exp_count = sum(1 for indicator in self.experience_indicators if indicator in text)
        
        level = "entry"
        if max_years >= 5 or exp_count >= 8:
            level = "senior"
        elif max_years >= 2 or exp_count >= 4:
            level = "mid"
        
        return {
            "estimated_years": max_years,
            "level": level,
            "experience_indicators": exp_count
        }
    
    def _extract_education(self, text: str) -> Dict[str, Any]:
        """Extract education information"""
        degrees = ["bachelor", "master", "phd", "doctorate", "mba", "bs", "ba", "ms", "ma"]
        found_degrees = [degree for degree in degrees if degree in text]
        
        return {
            "degrees": found_degrees,
            "has_degree": len(found_degrees) > 0,
            "highest_level": found_degrees[-1] if found_degrees else "not_specified"
        }
    
    def _calculate_job_fit(self, resume_text: str, job_description: str) -> float:
        """Calculate simple job fit score"""
        if not job_description:
            return 0.7
        
        job_words = set(job_description.lower().split())
        resume_words = set(resume_text.split())
        
        # Simple word overlap calculation
        overlap = len(job_words.intersection(resume_words))
        total_unique = len(job_words.union(resume_words))
        
        return min(0.95, overlap / max(total_unique, 1) * 3)  # Scale up the score
    
    def _identify_strengths(self, skills: Dict, experience: Dict) -> List[str]:
        """Identify candidate strengths"""
        strengths = []
        
        if skills:
            strengths.append(f"Diverse skill set across {len(skills)} areas")
        
        exp_level = experience.get("level", "entry")
        if exp_level == "senior":
            strengths.append("Extensive professional experience")
        elif exp_level == "mid":
            strengths.append("Solid professional background")
        
        if experience.get("estimated_years", 0) > 0:
            strengths.append(f"Approximately {experience['estimated_years']} years of experience")
        
        return strengths or ["Professional background"]
    
    def _identify_concerns(self, skills: Dict, experience: Dict) -> List[str]:
        """Identify potential concerns"""
        concerns = []
        
        if not skills:
            concerns.append("Limited technical skills identified")
        
        if experience.get("level") == "entry":
            concerns.append("Early career professional")
        
        return concerns or ["Manual review recommended"]
    
    def _generate_interview_recommendations(self, skills: Dict) -> List[str]:
        """Generate interview recommendations"""
        recommendations = ["Verify technical skills mentioned in resume"]
        
        if "programming" in skills:
            recommendations.append("Include coding exercise or technical discussion")
        
        if "management" in skills:
            recommendations.append("Discuss leadership and team management experience")
        
        recommendations.append("Assess cultural fit and communication skills")
        
        return recommendations
    
    def _calculate_skill_match(self, candidate_skills: Dict, required_skills: List[str]) -> float:
        """Calculate skill match percentage"""
        if not required_skills:
            return 0.8
        
        candidate_skill_list = []
        for skills in candidate_skills.values():
            candidate_skill_list.extend([s.lower() for s in skills])
        
        required_lower = [s.lower() for s in required_skills]
        matches = sum(1 for req in required_lower if any(req in candidate for candidate in candidate_skill_list))
        
        return matches / len(required_skills) if required_skills else 0.8
    
    def _identify_match_strengths(self, candidate_skills: Dict, required_skills: List[str]) -> List[str]:
        """Identify matching strengths"""
        strengths = []
        
        for category, skills in candidate_skills.items():
            if skills:
                strengths.append(f"Strong {category} skills")
        
        return strengths or ["General professional competency"]
    
    def _identify_skill_gaps(self, candidate_skills: Dict, required_skills: List[str]) -> List[str]:
        """Identify skill gaps"""
        candidate_skill_list = []
        for skills in candidate_skills.values():
            candidate_skill_list.extend([s.lower() for s in skills])
        
        gaps = []
        for req in required_skills:
            if not any(req.lower() in candidate for candidate in candidate_skill_list):
                gaps.append(req)
        
        return gaps[:5]  # Limit to top 5 gaps
    
    def _generate_recommendation(self, fit_score: float) -> str:
        """Generate hiring recommendation"""
        if fit_score >= 8:
            return "strong_candidate"
        elif fit_score >= 6:
            return "proceed_with_interview"
        elif fit_score >= 4:
            return "consider_if_other_factors_strong"
        else:
            return "not_recommended"
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when processing fails"""
        return {
            "overall_match_score": 0.7,
            "technical_skills": {"general": ["Professional skills"]},
            "experience_analysis": {"level": "to_be_assessed", "estimated_years": 0},
            "education_analysis": {"has_degree": True, "degrees": []},
            "strengths": ["Resume submitted for review"],
            "concerns": ["Manual review required"],
            "interview_recommendations": ["Standard interview process"],
            "confidence_score": 0.5
        }
    
    def _fallback_questions(self) -> List[str]:
        """Fallback interview questions"""
        return [
            "Tell me about yourself and your background",
            "Why are you interested in this position?",
            "What are your key strengths?",
            "How do you handle challenges?",
            "Where do you see yourself in 5 years?"
        ]
    
    def _fallback_assessment(self) -> Dict[str, Any]:
        """Fallback assessment"""
        return {
            "fit_score": 6.0,
            "skill_match_percentage": 60.0,
            "experience_match": "to_be_verified",
            "strengths": ["Candidate applied for position"],
            "gaps": ["To be assessed during interview"],
            "recommendation": "proceed_with_interview"
        }


# Global service instance
claude_service = OpenSourceClaudeService()