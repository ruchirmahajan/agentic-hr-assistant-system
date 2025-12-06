"""
Custom exceptions for the HR Assistant application
"""
from fastapi import HTTPException, status


class HRAssistantException(Exception):
    """Base exception for HR Assistant"""
    pass


class AuthenticationError(HRAssistantException):
    """Authentication related errors"""
    pass


class AuthorizationError(HRAssistantException):
    """Authorization related errors"""
    pass


class ValidationError(HRAssistantException):
    """Data validation errors"""
    pass


class FileProcessingError(HRAssistantException):
    """File processing errors"""
    pass


class GDPRComplianceError(HRAssistantException):
    """GDPR compliance related errors"""
    pass


class AIServiceError(HRAssistantException):
    """AI service errors (free version)"""
    pass


# HTTP Exception helpers
def create_http_exception(
    status_code: int,
    detail: str,
    headers: dict = None
) -> HTTPException:
    """Create a standardized HTTP exception"""
    return HTTPException(
        status_code=status_code,
        detail=detail,
        headers=headers
    )


# Common HTTP exceptions
def unauthorized_exception(detail: str = "Not authenticated") -> HTTPException:
    return create_http_exception(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"}
    )


def forbidden_exception(detail: str = "Not enough permissions") -> HTTPException:
    return create_http_exception(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail
    )


def not_found_exception(detail: str = "Item not found") -> HTTPException:
    return create_http_exception(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail
    )


def validation_exception(detail: str = "Validation error") -> HTTPException:
    return create_http_exception(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=detail
    )