import time
import json
import uuid
from typing import Dict, Any, AsyncGenerator
import httpx
from app.services.base import LLMProvider, LLMProviderFactory
from app.schemas.base import (
    ChatCompletionRequest, 
    ChatCompletionResponse,
    ChatCompletionStreamResponse,
    Message,
    DeltaMessage,
    ChatCompletionStreamChoice,
    UsageInfo
)

@LLMProviderFactory.register("deepseek")
class DeepseekProvider(LLMProvider):
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
        # Deepseek uses the same format as OpenAI
        payload = request.model_dump(exclude_none=True)
        
        # Map model names if needed
        if not request.model.startswith("deepseek-"):
            payload["model"] = f"deepseek-{request.model}"
        
        return payload
    
    def process_response(self, response: Dict[str, Any]) -> ChatCompletionResponse:
        try:
            # Extract usage information
            usage_data = response.get("usage", {})
            if isinstance(usage_data, dict):
                usage = UsageInfo(
                    prompt_tokens=usage_data.get("prompt_tokens", 0),
                    completion_tokens=usage_data.get("completion_tokens", 0),
                    total_tokens=usage_data.get("total_tokens", 0)
                )
            else:
                usage = UsageInfo()  # Use default values
            
            # Create response with the processed usage
            return ChatCompletionResponse(
                id=response.get("id", f"chatcmpl-{str(uuid.uuid4())}"),
                created=response.get("created", int(time.time())),
                model=response.get("model", "unknown"),
                choices=[{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response.get("choices", [{}])[0].get("message", {}).get("content", "")
                    },
                    "finish_reason": response.get("choices", [{}])[0].get("finish_reason", "stop")
                }],
                usage=usage
            )
        except Exception as e:
            # If anything goes wrong, return a minimal valid response
            return ChatCompletionResponse(
                id=f"chatcmpl-{str(uuid.uuid4())}",
                created=int(time.time()),
                model="unknown",
                choices=[{
                    "index": 0,
                    "message": {"role": "assistant", "content": "Error processing response"},
                    "finish_reason": "error"
                }],
                usage=UsageInfo()
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
                        id=chunk.get("id", f"chatcmpl-{str(uuid.uuid4())}"),
                        created=chunk.get("created", int(time.time())),
                        model=chunk.get("model", "unknown"),
                        choices=[
                            ChatCompletionStreamChoice(
                                index=choice.get("index", 0),
                                delta=DeltaMessage(**choice.get("delta", {})),
                                finish_reason=choice.get("finish_reason")
                            )
                            for choice in chunk.get("choices", [])
                        ]
                    )
                except json.JSONDecodeError:
                    continue  # Skip malformed JSON 