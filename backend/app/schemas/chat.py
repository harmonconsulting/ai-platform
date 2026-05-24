from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str
    provider: str = "ollama"
    model: str = "qwen2.5:14b"


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
