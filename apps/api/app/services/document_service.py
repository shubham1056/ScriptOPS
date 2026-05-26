"""Document upload + processing service."""
from __future__ import annotations

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import DocumentStatus, EXTENSION_TO_MIME
from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.services.storage_service import get_storage
from app.utils.file_validator import validate_upload
from app.utils.text_extractor import extract_text

logger = get_logger(__name__)


class DocumentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = DocumentRepository(db)
        self.storage = get_storage()

    async def upload(self, owner_id: str, file: UploadFile) -> Document:
        content = await file.read()
        extension = validate_upload(file, len(content))

        storage_path = await self.storage.save(content=content, filename=file.filename or f"upload.{extension}")
        text = extract_text(content, extension)

        doc = Document(
            owner_id=owner_id,
            filename=file.filename or f"upload.{extension}",
            extension=extension,
            mime_type=EXTENSION_TO_MIME.get(extension, "application/octet-stream"),
            size_bytes=len(content),
            storage_path=storage_path,
            status=DocumentStatus.READY.value,
            extracted_text=text,
        )
        await self.repo.add(doc)
        await self.db.commit()
        logger.info("document_uploaded", id=doc.id, size=len(content))
        return doc

    async def list_for_owner(self, owner_id: str) -> list[Document]:
        return await self.repo.list_by_owner(owner_id)

    async def get_for_owner(self, doc_id: str, owner_id: str) -> Document:
        doc = await self.repo.get_for_owner(doc_id, owner_id)
        if not doc:
            raise NotFoundError("Document not found.")
        return doc

    async def delete(self, doc_id: str, owner_id: str) -> None:
        doc = await self.get_for_owner(doc_id, owner_id)
        try:
            await self.storage.delete(doc.storage_path)
        except Exception:
            logger.warning("storage_delete_failed", path=doc.storage_path)
        await self.repo.delete(doc.id)
        await self.db.commit()
