from typing import AsyncGenerator, Union

from app.core.providers.base import LLMProviderFactory
from app.schemas.base import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionStreamResponse
)


class ChatService:
    """Service for handling chat completions"""

    @staticmethod
    async def chat_completion(request: ChatCompletionRequest) -> Union[ChatCompletionResponse, AsyncGenerator[ChatCompletionStreamResponse, None]]:
        """Handle chat completion request"""
        provider = LLMProviderFactory.create(request.model)
        async with provider:
            if request.stream:
                return provider.chat_completion_stream(request)
            return await provider.chat_completion(request) 