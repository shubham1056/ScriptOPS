"""SOP repository."""
from __future__ import annotations

from sqlalchemy import desc, select

from app.models.sop import SOP
from app.repositories.base import BaseRepository


class SOPRepository(BaseRepository[SOP]):
    model = SOP

    async def list_by_owner(self, owner_id: str, *, limit: int = 50, offset: int = 0) -> list[SOP]:
        result = await self.db.execute(
            select(SOP)
            .where(SOP.owner_id == owner_id)
            .order_by(desc(SOP.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_for_owner(self, sop_id: str, owner_id: str) -> SOP | None:
        result = await self.db.execute(
            select(SOP).where(SOP.id == sop_id, SOP.owner_id == owner_id)
        )
        return result.scalar_one_or_none()
