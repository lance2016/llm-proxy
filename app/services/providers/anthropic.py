import time
import uuid
from typing import Dict, Any
from app.services.base import LLMProvider, LLMProviderFactory
from app.schemas.base import ChatCompletionRequest, ChatCompletionResponse, Message, ChatCompletionChoice

@LLMProviderFactory.register("anthropic")
class AnthropicProvider(LLMProvider):
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        headers = self.prepare_headers()
        payload = self.prepare_payload(request)
        
        async with self.client as client:
            response = await client.post(
                f"{self.api_base}/v1/messages",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return self.process_response(response.json())
    
    def prepare_headers(self) -> Dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
    
    def prepare_payload(self, request: ChatCompletionRequest) -> Dict[str, Any]:
        # Convert OpenAI format to Anthropic format
        messages = []
        for msg in request.messages:
            # Map OpenAI roles to Anthropic roles
            role = "assistant" if msg.role == "assistant" else "user"
            messages.append({"role": role, "content": msg.content})
        
        return {
            "model": request.model,
            "messages": messages,
            "max_tokens": request.max_tokens or 1000,
            "temperature": request.temperature,
            "stream": request.stream
        }
    
    def process_response(self, response: Dict[str, Any]) -> ChatCompletionResponse:
        # Convert Anthropic format to OpenAI format
        return ChatCompletionResponse(
            id=f"chatcmpl-{str(uuid.uuid4())}",
            created=int(time.time()),
            model=response["model"],
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=Message(
                        role="assistant",
                        content=response["content"][0]["text"]
                    ),
                    finish_reason=response.get("stop_reason", "stop")
                )
            ],
            usage={
                "prompt_tokens": response.get("usage", {}).get("input_tokens", 0),
                "completion_tokens": response.get("usage", {}).get("output_tokens", 0),
                "total_tokens": response.get("usage", {}).get("total_tokens", 0)
            }
        ) 