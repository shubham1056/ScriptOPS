"""Conversation + message schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.constants import MessageRole


class MessageCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=8000)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: MessageRole
    content: str
    tokens: int
    created_at: datetime


class ConversationCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    sop_id: str | None = None


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    sop_id: str | None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []
