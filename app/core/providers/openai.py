from app.core.providers.base import LLMProviderFactory
from app.core.config.settings import get_settings
from app.schemas.base import ChatCompletionRequest
from .base_openai import OpenAICompatibleProvider

@LLMProviderFactory.register("openai")
class OpenAIProvider(OpenAICompatibleProvider):
    """OpenAI API provider"""

    @classmethod
    def from_settings(cls) -> "OpenAIProvider":
        """Create provider instance from settings"""
        settings = get_settings()
        return cls(
            api_key=settings.openai_api_key,
            api_base=settings.openai_api_base,
            timeout=settings.openai_timeout
        )