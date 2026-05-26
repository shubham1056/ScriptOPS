"""Document schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.constants import DocumentStatus


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    extension: str
    mime_type: str
    size_bytes: int
    status: DocumentStatus
    error_message: str | None = None
    created_at: datetime
