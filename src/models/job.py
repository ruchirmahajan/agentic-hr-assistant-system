"""
Job model for job postings and requirements
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from ..core.database import Base


class Job(Base):
    """Job posting model"""
    __tablename__ = "jobs"
    # Removed schema for SQLite compatibility
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=False)
    department = Column(String(100), nullable=False)
    location = Column(String(200), nullable=False)
    employment_type = Column(String(50), nullable=False)  # full-time, part-time, contract
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    experience_level = Column(String(50), nullable=False)  # entry, mid, senior
    skills_required = Column(Text, nullable=True)  # JSON string of skills
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_urgent = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(36), nullable=True)  # Removed ForeignKey constraint for demo
    
    # Relationships (commented out due to removed FK)
    # creator = relationship("User", back_populates="jobs_created")
    applications = relationship("Application", back_populates="job")
    
    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', department='{self.department}')>"