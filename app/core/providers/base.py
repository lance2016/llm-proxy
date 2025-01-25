import time
import json
from typing import AsyncGenerator, Any, Callable, TypeVar, Dict, List, Type, ClassVar, Optional
import httpx
from abc import ABC, abstractmethod
from app.schemas.base import (
    ChatCompletionRequest, 
    ChatCompletionResponse,
    ChatCompletionStreamResponse,
    ChatCompletionStreamChoice,
    DeltaMessage,
    UsageInfo,
    Message
)
from app.core.config.settings import get_settings
from app.core.exceptions import ProviderNotFoundError

T = TypeVar('T')

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Execute chat completion request"""
        pass
    
    @abstractmethod
    async def chat_completion_stream(self, request: ChatCompletionRequest) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        """Execute streaming chat completion request"""
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()

    async def cleanup(self):
        """Cleanup resources"""
        pass

class LLMProviderFactory:
    """Factory for creating LLM providers"""
    
    _providers: ClassVar[Dict[str, Type[LLMProvider]]] = {}
    
    @classmethod
    def register(cls, prefix: str):
        """Register provider class with model name prefix"""
        def wrapper(provider_cls: Type[LLMProvider]) -> Type[LLMProvider]:
            cls._providers[prefix] = provider_cls
            return provider_cls
        return wrapper
    
    @classmethod
    def create(cls, model: str) -> LLMProvider:
        """Create provider instance for model"""
        for prefix, provider_cls in cls._providers.items():
            if model.startswith(prefix):
                if hasattr(provider_cls, 'from_settings'):
                    return provider_cls.from_settings()
                return provider_cls()
        raise ValueError(f"No provider found for model: {model}") 