from typing import Any, Dict, Optional
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

class AppError(HTTPException):
    """Base exception for application errors"""
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dict format"""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
                "status_code": self.status_code
            }
        }


class ValidationError(AppError):
    """Validation error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message=message,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(AppError):
    """Resource not found error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message,
            error_code="NOT_FOUND",
            details=details
        )


class RateLimitError(AppError):
    """Rate limit exceeded error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )


class UnauthorizedError(AppError):
    """Unauthorized error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            error_code="UNAUTHORIZED",
            details=details
        )


class ForbiddenError(AppError):
    """Forbidden error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            error_code="FORBIDDEN",
            details=details
        )


class InternalError(AppError):
    """Internal server error"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=message,
            error_code="INTERNAL_ERROR",
            details=details
        )
        # Log internal errors
        logger.error(f"Internal error: {message}", extra={"details": details})


class LLMAPIException(HTTPException):
    """Base exception for LLM API"""
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[dict[str, str]] = None
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class ProviderNotFoundError(LLMAPIException):
    """Raised when LLM provider is not found"""
    def __init__(self, model: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No provider found for model: {model}"
        )


class ProviderAPIError(LLMAPIException):
    """Raised when provider API returns an error"""
    def __init__(
        self,
        provider: str,
        status_code: int,
        detail: str,
        url: Optional[str] = None
    ) -> None:
        message = f"Error from {provider} API"
        if url:
            message += f" ({url})"
        message += f": {detail}"
        if status_code == 401:
            message += "\nPlease check your API key configuration"
        elif status_code == 403:
            message += "\nPlease check your API permissions"
        elif status_code == 429:
            message += "\nRate limit exceeded"
            
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=message
        ) 