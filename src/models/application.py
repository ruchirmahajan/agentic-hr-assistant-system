"""
Application model for job applications
"""
from sqlalchemy import Column, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from ..core.database import Base


class Application(Base):
    """Job application model"""
    __tablename__ = "applications"
    # Removed schema for SQLite compatibility
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    
    # Application status
    status = Column(String(50), nullable=False, default="applied")  # applied, screening, interview, hired, rejected
    
    # AI Analysis Results
    ai_score = Column(Float, nullable=True)  # Overall AI matching score (0-100)
    skills_match_score = Column(Float, nullable=True)
    experience_match_score = Column(Float, nullable=True)
    education_match_score = Column(Float, nullable=True)
    
    # AI Analysis Details
    ai_analysis = Column(Text, nullable=True)  # JSON string with detailed analysis
    matching_skills = Column(Text, nullable=True)  # JSON array of matching skills
    missing_skills = Column(Text, nullable=True)  # JSON array of missing skills
    ai_recommendation = Column(Text, nullable=True)  # AI recommendation text
    
    # Interview and Notes
    interview_notes = Column(Text, nullable=True)
    hr_notes = Column(Text, nullable=True)
    hiring_manager_notes = Column(Text, nullable=True)
    
    # Timestamps
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    interviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Flags
    is_flagged = Column(Boolean, default=False, nullable=False)
    is_shortlisted = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    
    def __repr__(self):
        return f"<Application(id={self.id}, candidate_id={self.candidate_id}, job_id={self.job_id}, status='{self.status}')>"