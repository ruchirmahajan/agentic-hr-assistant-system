"""
Document model for candidate document management
Supports multiple document types: Resume, Identity, Marksheets, Experience Letters, etc.
"""
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid
import enum


from ..core.database import Base


class DocumentType(str, enum.Enum):
    """Types of documents that can be uploaded"""
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    IDENTITY_PROOF = "identity_proof"  # Passport, Aadhaar, Driver's License, etc.
    ADDRESS_PROOF = "address_proof"
    EDUCATION_CERTIFICATE = "education_certificate"
    MARKSHEET = "marksheet"
    DEGREE_CERTIFICATE = "degree_certificate"
    EXPERIENCE_LETTER = "experience_letter"
    RELIEVING_LETTER = "relieving_letter"
    SALARY_SLIP = "salary_slip"
    OFFER_LETTER = "offer_letter"
    PORTFOLIO = "portfolio"
    CERTIFICATION = "certification"
    REFERENCE_LETTER = "reference_letter"
    BACKGROUND_CHECK = "background_check"
    MEDICAL_CERTIFICATE = "medical_certificate"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    """Document verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"
    UNDER_REVIEW = "under_review"


class DocumentAccessLevel(str, enum.Enum):
    """Who can access this document"""
    HR_ONLY = "hr_only"              # Only HR team
    PANEL_VIEW = "panel_view"        # Interview panels can view
    RESTRICTED = "restricted"         # Specific users only
    ALL_INTERVIEWERS = "all_interviewers"  # All interviewers in the process


class CandidateDocument(Base):
    """Document storage model for candidate documents"""
    __tablename__ = "candidate_documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to candidate
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    
    # Document metadata
    document_type = Column(String(50), nullable=False)  # From DocumentType enum
    document_subtype = Column(String(100), nullable=True)  # E.g., "Passport", "10th Marksheet"
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)  # UUID-based secure filename
    file_path = Column(String(500), nullable=False)  # Relative path in storage
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(100), nullable=False)
    file_extension = Column(String(20), nullable=False)
    
    # File integrity
    checksum = Column(String(64), nullable=True)  # SHA-256 hash for integrity verification
    
    # Document details
    document_number = Column(String(100), nullable=True)  # For ID docs: passport number, etc.
    issue_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    issuing_authority = Column(String(255), nullable=True)
    
    # For education documents
    institution_name = Column(String(255), nullable=True)
    year_of_passing = Column(Integer, nullable=True)
    grade_percentage = Column(String(50), nullable=True)
    
    # For experience documents
    company_name = Column(String(255), nullable=True)
    designation = Column(String(255), nullable=True)
    period_from = Column(DateTime, nullable=True)
    period_to = Column(DateTime, nullable=True)
    
    # Verification and status
    status = Column(String(30), default=DocumentStatus.PENDING.value)
    verification_notes = Column(Text, nullable=True)
    verified_by = Column(String(36), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Access control
    access_level = Column(String(30), default=DocumentAccessLevel.PANEL_VIEW.value)
    allowed_users = Column(JSON, default=list)  # Specific user IDs if restricted
    
    # Audit fields
    upload_ip = Column(String(45), nullable=True)
    download_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime, nullable=True)
    last_accessed_by = Column(String(36), nullable=True)
    
    # Version control
    version = Column(Integer, default=1)
    is_latest = Column(Boolean, default=True)
    previous_version_id = Column(String(36), nullable=True)
    
    # Soft delete
    is_active = Column(Boolean, default=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(String(36), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    uploaded_by = Column(String(36), nullable=True)
    
    # Tags for searching
    tags = Column(JSON, default=list)
    
    # AI analysis results (if applicable)
    ai_extracted_data = Column(JSON, nullable=True)  # OCR or AI-extracted info
    
    # Relationships
    candidate = relationship("Candidate", back_populates="documents")
    access_logs = relationship("DocumentAccessLog", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CandidateDocument(id='{self.id}', type='{self.document_type}', candidate='{self.candidate_id}')>"
    
    @property
    def is_expired(self) -> bool:
        """Check if document has expired"""
        if self.expiry_date:
            return datetime.utcnow() > self.expiry_date
        return False
    
    @property
    def file_size_formatted(self) -> str:
        """Return human-readable file size"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
    
    def can_access(self, user_id: str, user_role: str, panel_ids: List[str] = None) -> bool:
        """Check if a user can access this document"""
        # HR can always access
        if user_role in ["hr", "admin", "super_admin"]:
            return True
        
        # Check access level
        if self.access_level == DocumentAccessLevel.HR_ONLY.value:
            return False
        
        if self.access_level == DocumentAccessLevel.RESTRICTED.value:
            return user_id in (self.allowed_users or [])
        
        if self.access_level in [DocumentAccessLevel.PANEL_VIEW.value, DocumentAccessLevel.ALL_INTERVIEWERS.value]:
            return True  # Panel members can view
        
        return False


class DocumentAccessLog(Base):
    """Audit log for document access - GDPR compliance"""
    __tablename__ = "document_access_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    document_id = Column(String(36), ForeignKey("candidate_documents.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), nullable=False)
    user_name = Column(String(200), nullable=True)
    user_role = Column(String(50), nullable=True)
    
    action = Column(String(50), nullable=False)  # view, download, print, share
    action_details = Column(JSON, nullable=True)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    accessed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Context
    access_reason = Column(String(255), nullable=True)  # interview, verification, etc.
    interview_id = Column(String(36), nullable=True)  # If accessed during interview
    
    # Relationships
    document = relationship("CandidateDocument", back_populates="access_logs")

    def __repr__(self):
        return f"<DocumentAccessLog(document='{self.document_id}', user='{self.user_id}', action='{self.action}')>"


class DocumentTemplate(Base):
    """Templates for document requirements per job/role"""
    __tablename__ = "document_templates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Can be linked to specific job or department
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Required documents
    required_documents = Column(JSON, nullable=False)  # List of document types required
    optional_documents = Column(JSON, default=list)  # List of optional document types
    
    # Validation rules
    validation_rules = Column(JSON, default=dict)  # E.g., {"resume": {"max_size": 5, "required": true}}
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(36), nullable=True)

    def __repr__(self):
        return f"<DocumentTemplate(id='{self.id}', name='{self.name}')>"
