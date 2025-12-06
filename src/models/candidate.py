"""
Candidate model with encrypted PII and GDPR compliance
"""
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text, Integer, Date, LargeBinary
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, date
from typing import Optional, Dict, Any
import uuid

from ..core.database import Base
from ..core.security import security_utils, audit_logger


class Candidate(Base):
    """Candidate model with GDPR-compliant encrypted PII storage"""
    __tablename__ = "candidates"
    # Removed schema for SQLite compatibility
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Encrypted PII fields
    encrypted_email = Column(LargeBinary, nullable=False)
    encrypted_phone = Column(LargeBinary, nullable=True)
    encrypted_full_name = Column(LargeBinary, nullable=False)
    encrypted_address = Column(LargeBinary, nullable=True)
    
    # Non-PII profile data
    experience_years = Column(Integer, nullable=True)
    current_position = Column(String(255), nullable=True)
    current_company = Column(String(255), nullable=True)
    skills = Column(JSON, default=list)  # List of skills
    education = Column(JSON, default=dict)  # Education details
    
    # Resume analysis results (cached from Claude)
    ai_analysis = Column(JSON, nullable=True)
    skills_extracted = Column(JSON, default=list)
    
    # GDPR Compliance fields
    consent_status = Column(JSON, nullable=False, default=lambda: {
        "data_processing": True,
        "resume_analysis": True,
        "communication": True,
        "data_retention": True,
        "consent_date": datetime.utcnow().isoformat(),
        "consent_version": "1.0"
    })
    
    data_retention_date = Column(Date, nullable=True)
    gdpr_flags = Column(JSON, default=dict)
    
    # Source and tracking
    source = Column(String(100), nullable=True)  # LinkedIn, referral, etc.
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(36), nullable=True)  # User who created
    
    # Relationships
    applications = relationship("Application", back_populates="candidate")
    documents = relationship("CandidateDocument", back_populates="candidate", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Candidate(id='{self.id}')>"
    
    @property
    def email(self) -> str:
        """Decrypt and return email (with audit logging)"""
        audit_logger.log_pii_access(
            user_id="system",  # To be updated with actual user
            candidate_id=str(self.id),
            field_name="email",
            action="read"
        )
        return security_utils.decrypt_pii(self.encrypted_email)
    
    @email.setter
    def email(self, value: str):
        """Encrypt and store email"""
        self.encrypted_email = security_utils.encrypt_pii(value)
        audit_logger.log_pii_access(
            user_id="system",
            candidate_id=str(self.id),
            field_name="email",
            action="update"
        )
    
    @property
    def phone(self) -> Optional[str]:
        """Decrypt and return phone (with audit logging)"""
        if not self.encrypted_phone:
            return None
        
        audit_logger.log_pii_access(
            user_id="system",
            candidate_id=str(self.id),
            field_name="phone",
            action="read"
        )
        return security_utils.decrypt_pii(self.encrypted_phone)
    
    @phone.setter
    def phone(self, value: Optional[str]):
        """Encrypt and store phone"""
        if value:
            self.encrypted_phone = security_utils.encrypt_pii(value)
        else:
            self.encrypted_phone = None
        
        audit_logger.log_pii_access(
            user_id="system",
            candidate_id=str(self.id),
            field_name="phone",
            action="update"
        )
    
    @property
    def full_name(self) -> str:
        """Decrypt and return full name (with audit logging)"""
        audit_logger.log_pii_access(
            user_id="system",
            candidate_id=str(self.id),
            field_name="full_name",
            action="read"
        )
        return security_utils.decrypt_pii(self.encrypted_full_name)
    
    @full_name.setter
    def full_name(self, value: str):
        """Encrypt and store full name"""
        self.encrypted_full_name = security_utils.encrypt_pii(value)
        audit_logger.log_pii_access(
            user_id="system",
            candidate_id=str(self.id),
            field_name="full_name",
            action="update"
        )
    
    @property
    def address(self) -> Optional[str]:
        """Decrypt and return address (with audit logging)"""
        if not self.encrypted_address:
            return None
        
        audit_logger.log_pii_access(
            user_id="system",
            candidate_id=str(self.id),
            field_name="address",
            action="read"
        )
        return security_utils.decrypt_pii(self.encrypted_address)
    
    @address.setter
    def address(self, value: Optional[str]):
        """Encrypt and store address"""
        if value:
            self.encrypted_address = security_utils.encrypt_pii(value)
        else:
            self.encrypted_address = None
        
        audit_logger.log_pii_access(
            user_id="system",
            candidate_id=str(self.id),
            field_name="address",
            action="update"
        )
    
    def calculate_retention_date(self) -> date:
        """Calculate GDPR data retention date"""
        from ..core.config import settings
        from dateutil.relativedelta import relativedelta
        
        if not self.data_retention_date:
            self.data_retention_date = (
                datetime.utcnow().date() + 
                relativedelta(years=settings.DATA_RETENTION_YEARS)
            )
        
        return self.data_retention_date
    
    def can_be_deleted(self) -> bool:
        """Check if candidate data can be deleted per GDPR"""
        return (
            self.data_retention_date and 
            self.data_retention_date <= datetime.utcnow().date()
        )
    
    def anonymize_data(self):
        """Anonymize candidate data for GDPR compliance"""
        self.encrypted_email = security_utils.encrypt_pii("anonymized@deleted.com")
        self.encrypted_phone = None
        self.encrypted_full_name = security_utils.encrypt_pii("Deleted User")
        self.encrypted_address = None
        
        # Update GDPR flags
        self.gdpr_flags = self.gdpr_flags or {}
        self.gdpr_flags["anonymized"] = True
        self.gdpr_flags["anonymized_date"] = datetime.utcnow().isoformat()
        
        audit_logger.log_data_operation(
            user_id="system",
            operation="anonymize_candidate",
            details={"candidate_id": str(self.id)}
        )
    
    def to_dict(self, include_pii: bool = False) -> Dict[str, Any]:
        """Convert to dictionary, optionally including PII"""
        data = {
            "id": str(self.id),
            "experience_years": self.experience_years,
            "current_position": self.current_position,
            "current_company": self.current_company,
            "skills": self.skills,
            "education": self.education,
            "ai_analysis": self.ai_analysis,
            "skills_extracted": self.skills_extracted,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_pii:
            data.update({
                "email": self.email,
                "phone": self.phone,
                "full_name": self.full_name,
                "address": self.address,
            })
        
        return data