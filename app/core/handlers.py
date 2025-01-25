from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .exceptions import AppError
import logging

logger = logging.getLogger(__name__)

async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle application specific errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation errors"""
    details = []
    for error in exc.errors():
        details.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": details,
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
            }
        }
    )

async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unhandled exceptions"""
    # Log the error
    logger.exception("Unhandled exception occurred", exc_info=exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {
                    "type": type(exc).__name__,
                    "message": str(exc)
                } if not isinstance(exc, AssertionError) else {},
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        }
    ) 