import platform
from datetime import datetime
from typing import Dict, Any

def get_system_info() -> Dict[str, Any]:
    """Get system information"""
    return {
        "version": "0.0.1",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": "Asia/Shanghai"
    }

def get_welcome_info() -> Dict[str, Any]:
    """Get welcome page information"""
    return {
        "message": "Welcome to LLM API Gateway!",
        "system_info": get_system_info(),
        "features": [
            "🤖 Multiple LLM Provider Support",
            "🔄 Automatic Failover",
            "⚡ Streaming Response",
            "🔒 Rate Limiting",
            "📊 Usage Statistics"
        ],
        "available_providers": [
            "OpenAI",
            "Deepseek",
            "More coming soon..."
        ],
        "links": {
            "documentation": "/docs",
            "openapi": "/openapi.json",
            "github": "https://github.com/lance2016",
            "author": "Lance"
        },
        "status": "�� Operational"
    } 