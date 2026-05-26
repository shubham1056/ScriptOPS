"""Conversation service — chat over an SOP with streaming responses."""
from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.azure_client import get_ai_client
from app.ai.prompts import SYSTEM_PROMPT_SOP
from app.constants import MessageRole
from app.core.exceptions import NotFoundError
from app.models.conversation import Conversation, Message
from app.repositories.conversation_repository import ConversationRepository, MessageRepository
from app.repositories.sop_repository import SOPRepository
from app.schemas.conversation import ConversationCreateRequest
from app.utils.sanitizer import sanitize_user_message


class ConversationService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.conversations = ConversationRepository(db)
        self.messages = MessageRepository(db)
        self.sops = SOPRepository(db)
        self.ai = get_ai_client()

    async def create(self, owner_id: str, payload: ConversationCreateRequest) -> Conversation:
        conv = Conversation(
            owner_id=owner_id,
            title=payload.title or "New Conversation",
            sop_id=payload.sop_id,
        )
        await self.conversations.add(conv)
        await self.db.commit()
        # Eager-load the relationship so Pydantic serialization doesn't trigger
        # a lazy load outside the async context (MissingGreenlet).
        await self.db.refresh(conv, attribute_names=["messages"])
        return conv

    async def list_for_owner(self, owner_id: str) -> list[Conversation]:
        return await self.conversations.list_by_owner(owner_id)

    async def get(self, conv_id: str, owner_id: str) -> Conversation:
        conv = await self.conversations.get_with_messages(conv_id, owner_id)
        if not conv:
            raise NotFoundError("Conversation not found.")
        return conv

    async def stream_response(self, conv_id: str, owner_id: str, user_message: str) -> AsyncIterator[str]:
        conv = await self.get(conv_id, owner_id)
        clean = sanitize_user_message(user_message)

        # persist user message
        user_msg = Message(conversation_id=conv.id, role=MessageRole.USER.value, content=clean)
        await self.messages.add(user_msg)
        await self.db.commit()

        # Build conversation context
        sop_context = ""
        if conv.sop_id:
            sop = await self.sops.get(conv.sop_id)
            if sop and sop.markdown:
                sop_context = f"\n\nCONTEXT — Current SOP:\n{sop.markdown}\n"

        history = "\n".join(f"{m.role.upper()}: {m.content}" for m in conv.messages)
        prompt = f"{history}\n\nUSER: {clean}{sop_context}\n\nRespond helpfully and concisely."

        chunks: list[str] = []
        async for token in self.ai.stream(system_prompt=SYSTEM_PROMPT_SOP, user_prompt=prompt):
            chunks.append(token)
            yield token

        # persist assistant message
        assistant_msg = Message(
            conversation_id=conv.id,
            role=MessageRole.ASSISTANT.value,
            content="".join(chunks),
        )
        await self.messages.add(assistant_msg)
        await self.db.commit()
