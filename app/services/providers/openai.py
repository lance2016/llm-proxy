import time
import json
from typing import Dict, Any, AsyncGenerator
import httpx
from app.services.base import LLMProvider, LLMProviderFactory
from app.schemas.base import (
    ChatCompletionRequest, 
    ChatCompletionResponse,
    ChatCompletionStreamResponse,
    ChatCompletionStreamChoice,
    DeltaMessage,
    UsageInfo
)

@LLMProviderFactory.register("openai")
class OpenAIProvider(LLMProvider):
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        headers = self.prepare_headers()
        payload = self.prepare_payload(request)
        
        client = await self.client
        response = await client.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30.0
        )
        response.raise_for_status()
        return self.process_response(response.json())
    
    async def chat_completion_stream(
        self, 
        request: ChatCompletionRequest
    ) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        headers = self.prepare_headers()
        payload = self.prepare_payload(request)
        payload["stream"] = True
        
        client = await self.client
        async with client.stream('POST',
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30.0
        ) as response:
            response.raise_for_status()
            async for chunk in self.process_stream_response(response):
                yield chunk
    
    def prepare_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def prepare_payload(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        return request.model_dump(exclude_none=True)
    
    def process_response(self, response: Dict[str, Any]) -> ChatCompletionResponse:
        # Extract usage information
        usage_data = response.get("usage", {})
        usage = UsageInfo(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0)
        )
        
        # Create response with the processed usage
        return ChatCompletionResponse(
            id=response["id"],
            created=response.get("created", int(time.time())),
            model=response["model"],
            choices=response["choices"],
            usage=usage
        )
    
    async def process_stream_response(
        self, 
        response: httpx.Response
    ) -> AsyncGenerator[ChatCompletionStreamResponse, None]:
        async for line in response.aiter_lines():
            if line.strip():
                if line.startswith("data: "):
                    line = line[6:]  # Remove "data: " prefix
                if line.strip() == "[DONE]":
                    break
                
                try:
                    chunk = json.loads(line)
                    yield ChatCompletionStreamResponse(
                        id=chunk["id"],
                        created=chunk.get("created", int(time.time())),
                        model=chunk["model"],
                        choices=[
                            ChatCompletionStreamChoice(
                                index=choice.get("index", 0),
                                delta=DeltaMessage(**choice.get("delta", {})),
                                finish_reason=choice.get("finish_reason")
                            )
                            for choice in chunk["choices"]
                        ]
                    )
                except json.JSONDecodeError:
                    continue  # Skip malformed JSON 