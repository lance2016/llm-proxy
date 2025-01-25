from functools import lru_cache
from typing import Dict, List, Optional, Any
import logging
import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    PROJECT_NAME: str = "FastAPI Application"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # CORS settings
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds (alias for RATE_LIMIT_WINDOW)
    
    # Logging settings
    LOG_DIR: str = "logs"
    LOG_LEVEL: int = logging.INFO
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # Environment specific settings
    ENV: str = os.getenv("ENV", "development")
    
    # OpenAI Provider
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_TIMEOUT: float = 30.0
    
    # Anthropic Provider
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_API_BASE: str = "https://api.anthropic.com"
    ANTHROPIC_TIMEOUT: float = 30.0
    
    # Deepseek Provider
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"
    DEEPSEEK_TIMEOUT: float = 30.0
    
    # Provider configurations
    PROVIDER_CONFIGS: Dict[str, Dict[str, str]] = {
        "gpt": {"provider": "openai", "api_key": "OPENAI_API_KEY", "api_base": "OPENAI_API_BASE"},
        "anthropic": {"provider": "anthropic", "api_key": "ANTHROPIC_API_KEY", "api_base": "ANTHROPIC_API_BASE"},
        "deepseek": {"provider": "deepseek", "api_key": "DEEPSEEK_API_KEY", "api_base": "DEEPSEEK_API_BASE"},
    }
    
    class Config:
        """Pydantic config"""
        env_file = ".env"
        case_sensitive = True

    @property
    def is_development(self) -> bool:
        return self.ENV.lower() == "development"

    @property
    def is_production(self) -> bool:
        return self.ENV.lower() == "production"

    @property
    def rate_limit_window(self) -> int:
        """Alias for RATE_LIMIT_PERIOD for backward compatibility"""
        return self.RATE_LIMIT_PERIOD

    def validate(self) -> None:
        """Validate settings"""
        if self.is_production:
            assert not self.DEBUG, "DEBUG should be False in production"
            assert "*" not in self.ALLOWED_HOSTS, "ALLOWED_HOSTS should be explicitly set in production"
            assert self.RATE_LIMIT_ENABLED, "Rate limiting should be enabled in production"
            
            # Validate at least one API key is set in production
            api_keys = [
                self.OPENAI_API_KEY,
                self.ANTHROPIC_API_KEY,
                self.DEEPSEEK_API_KEY
            ]
            assert any(api_keys), "At least one API key must be set in production"


# Global settings instance
_settings = None

def get_settings() -> Settings:
    """Get cached settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
        # Validate settings
        _settings.validate()
    return _settings 