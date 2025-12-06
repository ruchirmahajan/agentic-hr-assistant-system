"""
User model for authentication and authorization
"""
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Enum as SQLEnum, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

from ..core.database import Base


class UserRole(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    HR_MANAGER = "hr_manager"
    RECRUITER = "recruiter"
    INTERVIEWER = "interviewer"
    READONLY = "readonly"


class User(Base):
    """User model with GDPR compliance"""
    __tablename__ = "users"
    # Removed schema for SQLite compatibility
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Authentication
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Role and permissions
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.READONLY)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # GDPR and audit fields
    consent_status = Column(JSON, nullable=False, default=lambda: {
        "data_processing": True,
        "analytics": False,
        "marketing": False,
        "consent_date": datetime.utcnow().isoformat()
    })
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Security
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    password_reset_token = Column(String(255))
    password_reset_expires = Column(DateTime(timezone=True))
    
    # Relationships (commented out due to removed FK in Job model)
    # jobs_created = relationship("Job", back_populates="creator")

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        from ..core.rbac import ROLE_PERMISSIONS, Permission
        
        try:
            perm_enum = Permission(permission)
            return perm_enum in ROLE_PERMISSIONS.get(self.role, set())
        except ValueError:
            return False
    
    def is_account_locked(self) -> bool:
        """Check if account is locked"""
        return (
            self.locked_until is not None 
            and self.locked_until > datetime.utcnow()
        )