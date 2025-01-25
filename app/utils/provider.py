from typing import Optional
import logging
from app.core.config.settings import get_settings
from app.services.base import LLMProviderFactory

# Get settings instance
settings = get_settings()

logger = logging.getLogger(__name__)

def get_provider_by_model(model: str):
    """Get the appropriate provider based on the model name prefix."""
    try:
        model_prefix = model.split("-")[0].lower()
        
        provider_config = settings.PROVIDER_CONFIGS.get(model_prefix)
        if not provider_config:
            raise ValueError(f"Unsupported model prefix: {model_prefix}")
        
        provider_name = provider_config["provider"]
        api_key = getattr(settings, provider_config["api_key"])
        api_base = getattr(settings, provider_config["api_base"])
        
        if not api_key:
            raise ValueError(f"API key not configured for provider: {provider_name}")
        
        provider = LLMProviderFactory.create(provider_name, api_key, api_base)
        if not provider:
            raise ValueError(f"Provider {provider_name} is not properly registered")
            
        return provider
        
    except Exception as e:
        logger.error(f"Error creating provider for model {model}: {str(e)}")
        raise ValueError(f"Failed to create provider for model {model}: {str(e)}") 