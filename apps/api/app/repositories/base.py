"""Generic async base repository."""
from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """CRUD scaffolding shared by all repositories."""

    model: type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, entity_id: str) -> ModelT | None:
        result = await self.db.execute(select(self.model).where(self.model.id == entity_id))  # type: ignore[attr-defined]
        return result.scalar_one_or_none()

    async def list(self, *, limit: int = 50, offset: int = 0) -> list[ModelT]:
        result = await self.db.execute(select(self.model).limit(limit).offset(offset))
        return list(result.scalars().all())

    async def add(self, entity: ModelT) -> ModelT:
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def delete(self, entity_id: str) -> None:
        await self.db.execute(delete(self.model).where(self.model.id == entity_id))  # type: ignore[attr-defined]

    async def commit(self) -> None:
        await self.db.commit()
