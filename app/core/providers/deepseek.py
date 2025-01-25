from typing import Dict
from app.core.config.settings import get_settings
from .base_openai import OpenAICompatibleProvider
from .base import LLMProviderFactory
from app.schemas.base import ChatCompletionRequest


@LLMProviderFactory.register("deepseek")
class DeepseekProvider(OpenAICompatibleProvider):
    """Deepseek API provider that is OpenAI compatible"""

    @classmethod
    def from_settings(cls) -> "DeepseekProvider":
        """Create provider instance from settings"""
        settings = get_settings()
        return cls(
            api_key=settings.DEEPSEEK_API_KEY,
            api_base=settings.DEEPSEEK_API_BASE,
            timeout=settings.DEEPSEEK_TIMEOUT
        )

    def prepare_payload(self, request: ChatCompletionRequest) -> Dict:
        """Add deepseek- prefix to model if needed"""
        payload = super().prepare_payload(request)
        if not payload["model"].startswith("deepseek-"):
            payload["model"] = f"deepseek-{payload['model']}"
        return payload 