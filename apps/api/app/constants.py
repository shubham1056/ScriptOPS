"""Centralized constants for TranscribeOP backend."""
from __future__ import annotations

from enum import Enum
from typing import Final


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
API_V1_PREFIX: Final[str] = "/api/v1"
DOCS_URL: Final[str] = "/docs"
REDOC_URL: Final[str] = "/redoc"
OPENAPI_URL: Final[str] = "/openapi.json"

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
TOKEN_TYPE_BEARER: Final[str] = "bearer"
ACCESS_TOKEN_SUBJECT: Final[str] = "access"
REFRESH_TOKEN_SUBJECT: Final[str] = "refresh"


class UserRole(str, Enum):
    """Role-based access control roles."""

    USER = "USER"
    EDITOR = "EDITOR"
    ADMIN = "ADMIN"


# ---------------------------------------------------------------------------
# File upload
# ---------------------------------------------------------------------------
ALLOWED_MIME_TYPES: Final[set[str]] = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
}

EXTENSION_TO_MIME: Final[dict[str, str]] = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt": "text/plain",
    "md": "text/markdown",
}


class DocumentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


class SOPStatus(str, Enum):
    QUEUED = "QUEUED"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


# ---------------------------------------------------------------------------
# AI
# ---------------------------------------------------------------------------
DEFAULT_CHUNK_TOKENS: Final[int] = 3000
DEFAULT_CHUNK_OVERLAP: Final[int] = 200
MAX_TRANSCRIPT_TOKENS: Final[int] = 200_000
GPT_ENCODING_NAME: Final[str] = "cl100k_base"

SOP_SECTIONS: Final[tuple[str, ...]] = (
    "Title",
    "Objective",
    "Scope",
    "Prerequisites",
    "Step-by-step Instructions",
    "Validation",
    "Troubleshooting",
    "Notes",
    "Risks",
    "Best Practices",
)

# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------
class AuditAction(str, Enum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    DOCUMENT_UPLOAD = "DOCUMENT_UPLOAD"
    SOP_GENERATE = "SOP_GENERATE"
    SOP_UPDATE = "SOP_UPDATE"
    SOP_DELETE = "SOP_DELETE"
    SOP_EXPORT = "SOP_EXPORT"
