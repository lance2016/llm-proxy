import time
import logging
import uuid
import contextvars
from typing import Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from starlette.types import ASGIApp, Message
from app.core.context import set_request_id, get_request_id

logger = logging.getLogger(__name__)

# Create a context variable for trace_id
request_id_var = contextvars.ContextVar("request_id", default=None)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Ensure our middleware runs first
        self.app = app
    
    def get_trace_id(self, request: Request) -> str:
        """Get or generate trace ID for request"""
        trace_id = request.headers.get("X-Request-ID")
        if not trace_id:
            trace_id = str(uuid.uuid4())
        return trace_id
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Get or generate trace ID and set it in context at the very beginning
        # This needs to happen before ANY logging
        trace_id = self.get_trace_id(request)
        request_id_var.set(trace_id)  # Set in context vars
        set_request_id(trace_id)  # Set in our app context
        
        # Add trace ID to request state and headers for downstream use
        request.state.trace_id = trace_id
        
        # Add trace ID to request headers
        headers = [(k.lower(), v) for k, v in request.headers.raw]
        if b"x-request-id" not in [k.lower() for k, _ in headers]:
            headers.append((b"x-request-id", trace_id.encode()))
        request.scope["headers"] = headers
        
        start_time = time.time()
        
        try:
            # Log request with details
            logger.info(
                "Request Details",
                extra={
                    "trace_id": trace_id,
                    "request": {
                        "method": request.method,
                        "path": request.url.path,
                        "query_params": str(request.query_params),
                        "client_ip": request.client.host if request.client else None,
                    }
                }
            )
            
            # Process request
            response = await call_next(request)
            
            # Add trace ID to response headers
            response.headers["X-Trace-ID"] = trace_id
            
            # Log response
            process_time = time.time() - start_time
            status_code = response.status_code
            logger.info(
                "Response Details",
                extra={
                    "trace_id": trace_id,
                    "response": {
                        "status_code": status_code,
                        "process_time": process_time
                    }
                }
            )
            
            return response
        except Exception as e:
            logger.exception(
                "Request failed",
                extra={
                    "trace_id": trace_id,
                    "error": str(e)
                }
            )
            raise 