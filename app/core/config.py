from typing import Dict, Any
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "LLM API Gateway"
    API_V1_STR: str = "/api/v1"
    
    # OpenAI Compatible Endpoints
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    
    # Anthropic Endpoints
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_API_BASE: str = "https://api.anthropic.com"
    
    # Deepseek Endpoints
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"
    
    # Provider configurations
    PROVIDER_CONFIGS: Dict[str, Dict[str, str]] = {
        "gpt": {"provider": "openai", "api_key": "OPENAI_API_KEY", "api_base": "OPENAI_API_BASE"},
        "anthropic": {"provider": "anthropic", "api_key": "ANTHROPIC_API_KEY", "api_base": "ANTHROPIC_API_BASE"},
        "deepseek": {"provider": "deepseek", "api_key": "DEEPSEEK_API_KEY", "api_base": "DEEPSEEK_API_BASE"},
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 