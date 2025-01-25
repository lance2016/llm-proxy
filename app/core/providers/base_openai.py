from typing import Dict, AsyncGenerator
import json
import time

from app.core.exceptions import ProviderAPIError
from app.schemas.base import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionStreamResponse,
    ChatCompletionStreamChoice,
    DeltaMessage,
    UsageInfo,
    ChatCompletionChoice,
    Message
)
from .base import LLMProvider
from .http_client import HTTPClientProvider

class OpenAICompatibleProvider(LLMProvider, HTTPClientProvider):
    """Base class for OpenAI-compatible providers"""

    def __init__(self, api_key: str, api_base: str, timeout: float = 30.0):
        super().__init__(api_key, api_base, timeout)
        self.chat_completion_url = f"{self.api_base}/chat/completions"

    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Execute chat completion request"""
        if request.stream:
            raise ValueError("Use chat_completion_stream for streaming requests")
        
        response = await self.make_request(
            method="POST",
            url=self.chat_completion_url,
            json=request.model_dump(exclude_none=True)
        )
        return self._process_completion_response(response.json())

    async def chat_completion_stream(
        self,
        request: ChatCompletionRequest
    ) -> AsyncGenerator[str, None]:
        """Execute streaming chat completion request"""
        request.stream = True
        
        async with self.stream_request(
            method="POST",
            url=self.chat_completion_url,
            json=request.model_dump(exclude_none=True)
        ) as response:
            async for chunk in self._process_stream_response(response):
                yield f"data: {json.dumps(chunk.model_dump())}\n\n"
            yield "data: [DONE]\n\n"

    def _process_completion_response(self, data: Dict) -> ChatCompletionResponse:
        """Process regular completion response"""
        usage_data = data.get("usage", {})
        usage = UsageInfo(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0)
        )
        
        choices = [
            ChatCompletionChoice(
                index=choice.get("index", i),
                message=Message(**choice["message"]),
                finish_reason=choice.get("finish_reason")
            )
            for i, choice in enumerate(data["choices"])
        ]
        
        return ChatCompletionResponse(
            id=data.get("id", f"chatcmpl-{time.time()}"),
            created=data.get("created", int(time.time())),
            model=data["model"],
            choices=choices,
            usage=usage
        )

    async def _process_stream_response(self, response) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        """Process streaming response"""
        async for line in response.aiter_lines():
            line = line.strip()
            if not line or line == "data: [DONE]":
                continue
                
            if line.startswith("data: "):
                line = line[6:]
                
            try:
                chunk = json.loads(line)
                choices = [
                    ChatCompletionStreamChoice(
                        index=choice.get("index", i),
                        delta=DeltaMessage(**choice.get("delta", {})),
                        finish_reason=choice.get("finish_reason")
                    )
                    for i, choice in enumerate(chunk["choices"])
                ]
                
                yield ChatCompletionStreamResponse(
                    id=chunk.get("id", f"chatcmpl-{time.time()}"),
                    created=chunk.get("created", int(time.time())),
                    model=chunk["model"],
                    choices=choices
                )
            except json.JSONDecodeError:
                continue 