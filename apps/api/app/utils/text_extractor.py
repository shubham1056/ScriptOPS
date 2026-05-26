"""Extract plain text from PDF / DOCX / TXT / MD."""
from __future__ import annotations

import io

import chardet
from docx import Document as DocxDocument
from pypdf import PdfReader

from app.core.exceptions import ValidationError


def _extract_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _extract_docx(data: bytes) -> str:
    doc = DocxDocument(io.BytesIO(data))
    return "\n".join(p.text for p in doc.paragraphs if p.text)


def _extract_text(data: bytes) -> str:
    detected = chardet.detect(data) or {}
    encoding = detected.get("encoding") or "utf-8"
    return data.decode(encoding, errors="replace")


_EXTRACTORS = {
    "pdf": _extract_pdf,
    "docx": _extract_docx,
    "txt": _extract_text,
    "md": _extract_text,
}


def extract_text(data: bytes, extension: str) -> str:
    """Extract plain text for the given file extension."""
    extractor = _EXTRACTORS.get(extension.lower())
    if not extractor:
        raise ValidationError(f"Cannot extract text from '.{extension}' files.")
    text = extractor(data).strip()
    if not text:
        raise ValidationError("Could not extract any text from the uploaded file.")
    return text
