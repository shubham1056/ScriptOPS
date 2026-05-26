"""SOP schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.constants import SOPStatus


class SOPSection(BaseModel):
    heading: str
    content: str


class SOPGenerateRequest(BaseModel):
    document_id: str
    title: str | None = Field(default=None, max_length=200)
    instructions: str | None = Field(default=None, max_length=2000)


class SOPUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    markdown: str | None = None
    sections: list[SOPSection] | None = None


class SOPResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str | None
    title: str
    status: SOPStatus
    markdown: str | None
    sections: list[SOPSection] | None
    tokens_used: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class SOPListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    status: SOPStatus
    created_at: datetime
    updated_at: datetime
