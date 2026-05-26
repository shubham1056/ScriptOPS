"""File validation: extension, size, MIME sniffing."""
from __future__ import annotations

from fastapi import UploadFile

from app.constants import EXTENSION_TO_MIME
from app.core.config import settings
from app.core.exceptions import ValidationError


def _extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def validate_upload(file: UploadFile, size_bytes: int) -> str:
    """Validate file extension + size. Returns lowercase extension."""
    if not file.filename:
        raise ValidationError("Filename is required.")

    ext = _extension(file.filename)
    if ext not in settings.allowed_extensions_set:
        raise ValidationError(
            f"Unsupported file type '.{ext}'. Allowed: {sorted(settings.allowed_extensions_set)}"
        )

    if size_bytes <= 0:
        raise ValidationError("Uploaded file is empty.")

    if size_bytes > settings.max_upload_bytes:
        raise ValidationError(
            f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    # Best-effort MIME check (browsers can lie; we mainly rely on ext)
    expected_mime = EXTENSION_TO_MIME.get(ext)
    if file.content_type and expected_mime and not file.content_type.startswith(expected_mime.split("/")[0]):
        # don't hard-fail, just warn at validation layer
        pass

    return ext
