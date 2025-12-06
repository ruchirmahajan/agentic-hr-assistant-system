"""
Security utilities for authentication and encryption
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import secrets
import hashlib
from fastapi import HTTPException, status
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Encryption for PII data
def get_fernet_key() -> Fernet:
    """Get Fernet encryption instance"""
    return Fernet(settings.ENCRYPTION_KEY.encode()[:44].ljust(44, b'='))

encryption_handler = get_fernet_key()


class SecurityUtils:
    """Security utilities for the application"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        try:
            encoded_jwt = jwt.encode(
                to_encode, 
                settings.SECRET_KEY, 
                algorithm=settings.JWT_ALGORITHM
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create access token"
            )
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError as e:
            logger.error(f"JWT validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def encrypt_pii(data: str) -> bytes:
        """Encrypt personally identifiable information"""
        try:
            return encryption_handler.encrypt(data.encode('utf-8'))
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    @staticmethod
    def decrypt_pii(encrypted_data: bytes) -> str:
        """Decrypt personally identifiable information"""
        try:
            return encryption_handler.decrypt(encrypted_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise
    
    @staticmethod
    def generate_secure_token() -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_file_content(content: bytes) -> str:
        """Generate SHA-256 hash of file content"""
        return hashlib.sha256(content).hexdigest()


class AuditLogger:
    """Audit logging for GDPR compliance"""
    
    @staticmethod
    def log_pii_access(user_id: str, candidate_id: str, field_name: str, action: str):
        """Log access to PII data"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "candidate_id": candidate_id,
            "field_name": field_name,
            "action": action,  # read, update, delete
            "ip_address": None,  # To be filled by middleware
        }
        logger.info(f"PII_ACCESS: {audit_entry}")
    
    @staticmethod
    def log_data_operation(user_id: str, operation: str, details: Dict[str, Any]):
        """Log data operations for audit trail"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "operation": operation,
            "details": details,
        }
        logger.info(f"DATA_OPERATION: {audit_entry}")


# Initialize security
security_utils = SecurityUtils()
audit_logger = AuditLogger()