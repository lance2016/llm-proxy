from typing import Optional, Dict, Any, Union
from httpx import AsyncClient, Response
from abc import ABC
from contextlib import asynccontextmanager
from app.core.context import get_request_id, request_id_var
import logging

logger = logging.getLogger(__name__)

class HTTPClientProvider(ABC):
    """Base class for providers that use HTTP client"""
    
    def __init__(self, api_key: str, api_base: str, timeout: float = 30.0):
        self.api_key = api_key
        self.api_base = api_base
        self.timeout = timeout
        self._client: Optional[AsyncClient] = None

    @property
    async def client(self) -> AsyncClient:
        """Lazy initialize HTTP client"""
        if self._client is None:
            event_hooks = {
                'request': [self.add_trace_id_to_log],
                'response': [self.add_trace_id_to_log]
            }
            self._client = AsyncClient(timeout=self.timeout, event_hooks=event_hooks)
        return self._client

    async def add_trace_id_to_log(self, request_or_response):
        """Add trace_id to request/response for logging"""
        trace_id = request_id_var.get()
        if hasattr(request_or_response, 'headers'):
            request_or_response.headers['X-Request-ID'] = trace_id

    async def cleanup(self):
        """Cleanup HTTP client"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def prepare_headers(self, **kwargs) -> Dict[str, str]:
        """Prepare request headers"""
        trace_id = request_id_var.get()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Request-ID": trace_id
        }
        headers.update(kwargs)
        logger.info(
            "Preparing request headers",
            extra={"trace_id": trace_id}
        )
        return headers

    @asynccontextmanager
    async def stream_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """Make streaming HTTP request"""
        request_headers = headers or self.prepare_headers()
        trace_id = request_headers.get("X-Request-ID")
        
        logger.info(
            "Making streaming request",
            extra={
                "trace_id": trace_id,
                "method": method,
                "url": url
            }
        )
        
        client = await self.client
        async with client.stream(
            method=method,
            url=url,
            headers=request_headers,
            timeout=self.timeout,
            **kwargs
        ) as response:
            response.raise_for_status()
            yield response

    async def make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Response:
        """Make regular HTTP request"""
        request_headers = headers or self.prepare_headers()
        trace_id = request_headers.get("X-Request-ID")
        
        logger.info(
            "Making request",
            extra={
                "trace_id": trace_id,
                "method": method,
                "url": url
            }
        )
        
        client = await self.client
        response = await client.request(
            method=method,
            url=url,
            headers=request_headers,
            timeout=self.timeout,
            **kwargs
        )
        response.raise_for_status()
        return response 