from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config.settings import get_settings
from app.core.exceptions import RateLimitError
import time
import asyncio
from collections import defaultdict


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests"""
    
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        self.requests = defaultdict(list)  # client_ip -> list of timestamps
        self._cleanup_task = None
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Clean old requests
        current_time = time.time()
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip]
            if current_time - ts < self.settings.RATE_LIMIT_PERIOD
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.settings.RATE_LIMIT_REQUESTS:
            raise RateLimitError()
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        # Start cleanup task if not running
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_old_requests())
        
        return await call_next(request)
    
    async def _cleanup_old_requests(self):
        """Periodically clean up old requests"""
        while True:
            await asyncio.sleep(60)  # Clean up every minute
            current_time = time.time()
            for ip in list(self.requests.keys()):
                self.requests[ip] = [
                    ts for ts in self.requests[ip]
                    if current_time - ts < self.settings.RATE_LIMIT_PERIOD
                ]
                if not self.requests[ip]:
                    del self.requests[ip] 