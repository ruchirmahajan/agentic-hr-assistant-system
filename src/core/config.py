"""
Configuration management for the HR Assistant application
"""
from pydantic import validator
from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # Application
    APP_NAME: str = "Agentic HR Assistant"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    
    # Free Local Storage (instead of paid MinIO/S3)
    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = "./storage"
    UPLOAD_PATH: str = "./uploads"
    
    # Redis
    REDIS_URL: str
    REDIS_PASSWORD: Optional[str] = None
    
    # Open Source AI Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    OLLAMA_TIMEOUT: int = 120
    LOCAL_AI_BASE_URL: str = "http://localhost:8080/v1"
    LOCAL_AI_MODEL: str = "ggml-model-q4_0"
    HUGGINGFACE_API_KEY: Optional[str] = None
    AI_PROVIDER: str = "ollama"  # ollama, localai, or huggingface
    
    # Security
    SECRET_KEY: str
    ENCRYPTION_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    
    # GDPR Configuration
    DATA_RETENTION_YEARS: int = 7
    CONSENT_REQUIRED: bool = True
    AUDIT_LOG_RETENTION_YEARS: int = 10
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".doc", ".docx", ".txt"]
    
    # Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    
    @validator('DATABASE_URL')
    def validate_database_url(cls, v):
        # Support both PostgreSQL and SQLite for MVP
        if not (v.startswith('postgresql://') or v.startswith('sqlite')):
            raise ValueError('DATABASE_URL must be a PostgreSQL or SQLite connection string')
        return v
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v
    
    @validator('ENCRYPTION_KEY')
    def validate_encryption_key(cls, v):
        if len(v) < 32:
            raise ValueError('ENCRYPTION_KEY must be at least 32 characters long')
        return v
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env file


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings