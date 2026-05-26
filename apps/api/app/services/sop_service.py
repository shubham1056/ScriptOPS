"""SOP generation service."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.orchestrator import SOPOrchestrator
from app.constants import SOPStatus
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import get_logger
from app.models.sop import SOP
from app.repositories.document_repository import DocumentRepository
from app.repositories.sop_repository import SOPRepository
from app.schemas.sop import SOPGenerateRequest, SOPUpdateRequest

logger = get_logger(__name__)


class SOPService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = SOPRepository(db)
        self.documents = DocumentRepository(db)
        self.orchestrator = SOPOrchestrator()

    async def queue(self, owner_id: str, payload: SOPGenerateRequest) -> SOP:
        doc = await self.documents.get_for_owner(payload.document_id, owner_id)
        if not doc:
            raise NotFoundError("Source document not found.")
        if not doc.extracted_text:
            raise ValidationError("Document has no extracted text yet.")

        sop = SOP(
            owner_id=owner_id,
            document_id=doc.id,
            title=payload.title or doc.filename,
            status=SOPStatus.QUEUED.value,
        )
        await self.repo.add(sop)
        await self.db.commit()
        return sop

    async def process(self, sop_id: str, instructions: str | None) -> SOP:
        """Run the AI pipeline and persist results. Called by BackgroundTasks."""
        sop = await self.repo.get(sop_id)
        if not sop:
            raise NotFoundError("SOP not found.")
        doc = await self.documents.get(sop.document_id or "")
        if not doc or not doc.extracted_text:
            sop.status = SOPStatus.FAILED.value
            sop.error_message = "Source document missing extracted text."
            await self.db.commit()
            return sop

        sop.status = SOPStatus.GENERATING.value
        await self.db.commit()

        try:
            result = await self.orchestrator.generate(
                transcript=doc.extracted_text,
                title=sop.title,
                instructions=instructions,
            )
            sop.title = result.title
            sop.markdown = result.markdown
            sop.sections = [s.model_dump() for s in result.sections]
            sop.tokens_used = result.tokens_used
            sop.status = SOPStatus.COMPLETED.value
            sop.error_message = None
        except Exception as exc:  # noqa: BLE001
            logger.exception("sop_generation_failed", id=sop_id)
            sop.status = SOPStatus.FAILED.value
            sop.error_message = str(exc)[:1000]

        await self.db.commit()
        return sop

    async def list_for_owner(self, owner_id: str) -> list[SOP]:
        return await self.repo.list_by_owner(owner_id)

    async def get_for_owner(self, sop_id: str, owner_id: str) -> SOP:
        sop = await self.repo.get_for_owner(sop_id, owner_id)
        if not sop:
            raise NotFoundError("SOP not found.")
        return sop

    async def update(self, sop_id: str, owner_id: str, payload: SOPUpdateRequest) -> SOP:
        sop = await self.get_for_owner(sop_id, owner_id)
        if payload.title is not None:
            sop.title = payload.title
        if payload.markdown is not None:
            sop.markdown = payload.markdown
        if payload.sections is not None:
            sop.sections = [s.model_dump() for s in payload.sections]
        await self.db.commit()
        await self.db.refresh(sop)
        return sop

    async def delete(self, sop_id: str, owner_id: str) -> None:
        sop = await self.get_for_owner(sop_id, owner_id)
        await self.repo.delete(sop.id)
        await self.db.commit()
