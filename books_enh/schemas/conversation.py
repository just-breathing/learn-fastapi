from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    metadata: Optional[dict] = None


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)
    model: Optional[str] = None
    provider: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=16384)


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    model_used: Optional[str] = None
    provider_used: Optional[str] = None
    token_usage: Optional[dict] = None
    created_at: datetime


class ConversationHistoryResponse(BaseModel):
    conversation: ConversationResponse
    messages: list[MessageResponse]
    has_summary: bool = False
    total_messages: int = 0
