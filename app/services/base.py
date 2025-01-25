from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncGenerator, Union
import httpx
from app.schemas.base import (
    ChatCompletionRequest, 
    ChatCompletionResponse,
    ChatCompletionStreamResponse
)

class LLMProvider(ABC):
    def __init__(self, api_key: str, api_base: str):
        self.api_key = api_key
        self.api_base = api_base
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    async def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient()
        return self._client
    
    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None
    
    @abstractmethod
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Execute normal chat completion request"""
        pass
    
    @abstractmethod
    async def chat_completion_stream(
        self, 
        request: ChatCompletionRequest
    ) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        """Execute streaming chat completion request"""
        pass
    
    @abstractmethod
    def prepare_headers(self) -> Dict[str, str]:
        """Prepare HTTP headers for the request"""
        pass
    
    @abstractmethod
    def prepare_payload(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        """Convert the standard request to provider-specific format"""
        pass
    
    @abstractmethod
    def process_response(self, response: Dict[str, Any]) -> ChatCompletionResponse:
        """Convert provider-specific response to standard format"""
        pass
    
    @abstractmethod
    async def process_stream_response(
        self, 
        response: httpx.Response
    ) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        """Process streaming response"""
        pass
    
    async def __aenter__(self):
        await self.client  # Ensure client is initialized
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

class LLMProviderFactory:
    _providers: Dict[str, type] = {}
    
    @classmethod
    def register(cls, provider_name: str):
        def wrapper(provider_class: type):
            cls._providers[provider_name] = provider_class
            return provider_class
        return wrapper
    
    @classmethod
    def create(cls, provider_name: str, api_key: str, api_base: str) -> Optional[LLMProvider]:
        provider_class = cls._providers.get(provider_name)
        if provider_class:
            return provider_class(api_key, api_base)
        raise ValueError(f"Unknown provider: {provider_name}") 