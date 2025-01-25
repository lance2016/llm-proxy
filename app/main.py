from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.core.config.settings import get_settings
from app.core.middleware.request_logging import RequestLoggingMiddleware
from app.core.middleware.rate_limit import RateLimitMiddleware
from app.core.exceptions import AppError
from app.core.handlers import app_error_handler, validation_error_handler, generic_error_handler
from app.api.v1 import endpoints
from app.utils.system_info import get_welcome_info
from app.core.logging_config import setup_logging

# Get settings
settings = get_settings()

# Create application
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG
)

# Add exception handlers
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# Add logging middleware first to ensure trace_id is available
app.add_middleware(RequestLoggingMiddleware)

# Add other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(endpoints.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        **get_welcome_info()
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    # Initialize logging with settings from config
    setup_logging(
        log_dir=settings.LOG_DIR,
        max_bytes=settings.LOG_MAX_BYTES,
        backup_count=settings.LOG_BACKUP_COUNT,
        log_level=settings.LOG_LEVEL
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    # Cleanup resources if needed
    pass
