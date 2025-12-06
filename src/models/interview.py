"""
Interview Panel, Slot, and Schedule models for comprehensive interview management
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import Optional, List
import uuid
import enum

from ..core.database import Base


class InterviewLevel(enum.Enum):
    """Interview levels/rounds"""
    SCREENING = "screening"
    TECHNICAL_1 = "technical_1"
    TECHNICAL_2 = "technical_2"
    MANAGERIAL = "managerial"
    HR = "hr"
    FINAL = "final"


class InterviewStatus(enum.Enum):
    """Interview status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    NO_SHOW = "no_show"


class SlotStatus(enum.Enum):
    """Slot availability status"""
    AVAILABLE = "available"
    BOOKED = "booked"
    BLOCKED = "blocked"
    PAST = "past"


class InterviewPanel(Base):
    """Interview panel with interviewers for different levels"""
    __tablename__ = "interview_panels"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    level = Column(String(50), nullable=False)  # screening, technical_1, technical_2, managerial, hr, final
    department = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    # Panel configuration
    max_interviews_per_day = Column(Integer, default=5)
    interview_duration_minutes = Column(Integer, default=60)
    buffer_minutes = Column(Integer, default=15)  # Buffer between interviews
    
    # Interviewers (JSON list of interviewer details)
    interviewers = Column(JSON, default=list)  # [{id, name, email, role, is_lead}]
    
    # Skills this panel evaluates
    skills_evaluated = Column(JSON, default=list)
    
    # Evaluation criteria
    evaluation_criteria = Column(JSON, default=list)  # [{criterion, weight, max_score}]
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    slots = relationship("InterviewSlot", back_populates="panel", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="panel")
    
    def __repr__(self):
        return f"<InterviewPanel(id={self.id}, name='{self.name}', level='{self.level}')>"


class InterviewSlot(Base):
    """Available time slots for interviews"""
    __tablename__ = "interview_slots"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    panel_id = Column(String(36), ForeignKey("interview_panels.id"), nullable=False)
    
    # Time slot details
    date = Column(DateTime(timezone=True), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    
    # Status
    status = Column(String(20), default="available")  # available, booked, blocked, past
    
    # If booked, reference to the interview
    interview_id = Column(String(36), ForeignKey("interviews.id"), nullable=True)
    
    # Recurring slot configuration
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50), nullable=True)  # daily, weekly, biweekly
    recurrence_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    panel = relationship("InterviewPanel", back_populates="slots")
    interview = relationship("Interview", back_populates="slot", foreign_keys=[interview_id])
    
    def __repr__(self):
        return f"<InterviewSlot(id={self.id}, date={self.date}, status='{self.status}')>"


class Interview(Base):
    """Scheduled interviews linking candidates, jobs, and panels"""
    __tablename__ = "interviews"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # References
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False)
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=True)
    panel_id = Column(String(36), ForeignKey("interview_panels.id"), nullable=False)
    
    # Interview details
    level = Column(String(50), nullable=False)  # screening, technical_1, etc.
    round_number = Column(Integer, default=1)
    
    # Schedule
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    scheduled_start = Column(DateTime(timezone=True), nullable=False)
    scheduled_end = Column(DateTime(timezone=True), nullable=False)
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)
    
    # Location/Mode
    interview_mode = Column(String(50), default="video")  # video, phone, in_person
    meeting_link = Column(String(500), nullable=True)
    location = Column(String(200), nullable=True)
    
    # Status
    status = Column(String(20), default="scheduled")
    
    # Feedback and scores
    feedback = Column(JSON, nullable=True)  # {interviewer_id: {comments, scores}}
    overall_score = Column(Float, nullable=True)
    recommendation = Column(String(50), nullable=True)  # proceed, reject, hold, hire
    
    # Notes
    interviewer_notes = Column(Text, nullable=True)
    hr_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(36), nullable=True)
    
    # Relationships
    candidate = relationship("Candidate", backref="interviews")
    job = relationship("Job", backref="interviews")
    application = relationship("Application", backref="interviews")
    panel = relationship("InterviewPanel", back_populates="interviews")
    slot = relationship("InterviewSlot", back_populates="interview", foreign_keys="InterviewSlot.interview_id")
    
    def __repr__(self):
        return f"<Interview(id={self.id}, level='{self.level}', status='{self.status}')>"


class InterviewFeedback(Base):
    """Detailed feedback from individual interviewers"""
    __tablename__ = "interview_feedback"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String(36), ForeignKey("interviews.id"), nullable=False)
    
    # Interviewer details
    interviewer_id = Column(String(36), nullable=False)
    interviewer_name = Column(String(200), nullable=False)
    interviewer_role = Column(String(100), nullable=True)
    
    # Scores by criteria
    scores = Column(JSON, default=dict)  # {criterion: score}
    overall_score = Column(Float, nullable=True)
    
    # Feedback
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    comments = Column(Text, nullable=True)
    
    # Recommendation
    recommendation = Column(String(50), nullable=True)  # strong_yes, yes, maybe, no, strong_no
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<InterviewFeedback(id={self.id}, interview_id='{self.interview_id}')>"
