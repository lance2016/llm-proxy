from typing import List, Optional, Union, Dict, Any, Literal
from pydantic import BaseModel, Field

class Message(BaseModel):
    """Chat message"""
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    """Chat completion request"""
    model: str
    messages: List[Message]
    stream: bool = False
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None

class DeltaMessage(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None

class ChatCompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str] = None

class ChatCompletionStreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[str] = None

class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatCompletionResponse(BaseModel):
    """Chat completion response"""
    id: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: UsageInfo

class ChatCompletionStreamResponse(BaseModel):
    """Chat completion stream response"""
    id: str
    created: int
    model: str
    choices: List[ChatCompletionStreamChoice]

class ErrorResponse(BaseModel):
    error: Dict[str, Any] 