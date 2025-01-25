import contextvars
from typing import Optional

# Create a context variable for request_id
request_id_var = contextvars.ContextVar("request_id", default=None)

def get_request_id() -> Optional[str]:
    """Get request ID from context"""
    return request_id_var.get(None)

def set_request_id(request_id: str) -> None:
    """Set request ID in context"""
    request_id_var.set(request_id) 