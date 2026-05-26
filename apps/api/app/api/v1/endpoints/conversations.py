"""Conversation endpoints with SSE streaming."""
from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import StreamingResponse

from app.api.v1.deps import CurrentUser, DBSession
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationResponse,
    MessageCreateRequest,
)
from app.services import exporter
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreateRequest, user: CurrentUser, db: DBSession
) -> ConversationResponse:
    conv = await ConversationService(db).create(user.id, payload)
    return ConversationResponse.model_validate(conv)


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(user: CurrentUser, db: DBSession) -> list[ConversationResponse]:
    convs = await ConversationService(db).list_for_owner(user.id)
    return [ConversationResponse.model_validate(c) for c in convs]


@router.get("/{conv_id}", response_model=ConversationResponse)
async def get_conversation(conv_id: str, user: CurrentUser, db: DBSession) -> ConversationResponse:
    conv = await ConversationService(db).get(conv_id, user.id)
    return ConversationResponse.model_validate(conv)


@router.get("/{conv_id}/download")
async def download_conversation(
    conv_id: str,
    fmt: str,
    user: CurrentUser,
    db: DBSession,
) -> Response:
    """Download a conversation transcript as `md`, `docx`, or `pdf` (?fmt=...)."""
    if fmt not in ("md", "docx", "pdf"):
        raise HTTPException(status_code=400, detail="fmt must be one of: md, docx, pdf")
    conv = await ConversationService(db).get(conv_id, user.id)
    markdown_source = exporter.conversation_to_markdown(title=conv.title, messages=conv.messages)
    payload = exporter.render(fmt=fmt, title=conv.title, markdown_text=markdown_source)
    filename = exporter.safe_filename(conv.title, fmt)
    return Response(
        content=payload,
        media_type=exporter.MIME[fmt],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/{conv_id}/messages/stream")
async def send_message_stream(
    conv_id: str, payload: MessageCreateRequest, user: CurrentUser, db: DBSession
):
    service = ConversationService(db)

    async def event_source():
        async for token in service.stream_response(conv_id, user.id, payload.content):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_source(), media_type="text/event-stream")
