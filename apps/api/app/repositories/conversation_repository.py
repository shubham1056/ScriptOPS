"""Conversation + message repository."""
from __future__ import annotations

from sqlalchemy import asc, desc, select
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, Message
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    model = Conversation

    async def list_by_owner(self, owner_id: str, *, limit: int = 50, offset: int = 0) -> list[Conversation]:
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.owner_id == owner_id)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_with_messages(self, conv_id: str, owner_id: str) -> Conversation | None:
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conv_id, Conversation.owner_id == owner_id)
        )
        return result.scalar_one_or_none()


class MessageRepository(BaseRepository[Message]):
    model = Message

    async def list_for_conversation(self, conv_id: str) -> list[Message]:
        result = await self.db.execute(
            select(Message).where(Message.conversation_id == conv_id).order_by(asc(Message.created_at))
        )
        return list(result.scalars().all())
