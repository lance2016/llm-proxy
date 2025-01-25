from typing import Type
from app.core.exceptions import ProviderNotFoundError
from .base_openai import OpenAICompatibleProvider
from .deepseek import DeepseekProvider
from .openai import OpenAIProvider

class ProviderFactory:
    """Factory class to create LLM providers based on model name"""
    
    _providers: dict[str, Type[OpenAICompatibleProvider]] = {
        "deepseek": DeepseekProvider,
        "openai": OpenAIProvider,
    }
    
    @classmethod
    def create(cls, model: str) -> OpenAICompatibleProvider:
        """Create a provider instance based on model name"""
        # Extract provider name from model (e.g., "deepseek-chat" -> "deepseek")
        provider_name = model.split("-")[0].lower()
        
        provider_class = cls._providers.get(provider_name)
        if not provider_class:
            raise ProviderNotFoundError(f"No provider found for model: {model}")
            
        return provider_class.from_settings() 