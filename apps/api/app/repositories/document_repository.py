"""Document repository."""
from __future__ import annotations

from sqlalchemy import desc, select

from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    model = Document

    async def list_by_owner(self, owner_id: str, *, limit: int = 50, offset: int = 0) -> list[Document]:
        result = await self.db.execute(
            select(Document)
            .where(Document.owner_id == owner_id)
            .order_by(desc(Document.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_for_owner(self, doc_id: str, owner_id: str) -> Document | None:
        result = await self.db.execute(
            select(Document).where(Document.id == doc_id, Document.owner_id == owner_id)
        )
        return result.scalar_one_or_none()
