"""SOP endpoints — generate, retrieve, update, export, stream."""
from __future__ import annotations

import json

from fastapi import APIRouter, BackgroundTasks, HTTPException, Response, status
from fastapi.responses import StreamingResponse

from app.ai.orchestrator import SOPOrchestrator
from app.api.v1.deps import CurrentUser, DBSession
from app.core.database import AsyncSessionLocal
from app.schemas.sop import (
    SOPGenerateRequest,
    SOPListItem,
    SOPResponse,
    SOPUpdateRequest,
)
from app.services import exporter
from app.services.sop_service import SOPService

router = APIRouter(prefix="/sops", tags=["sops"])


async def _process_sop_job(sop_id: str, instructions: str | None) -> None:
    """Background-task entrypoint (uses its own session)."""
    async with AsyncSessionLocal() as db:
        await SOPService(db).process(sop_id, instructions)


@router.post("/generate", response_model=SOPResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_sop(
    payload: SOPGenerateRequest,
    background: BackgroundTasks,
    user: CurrentUser,
    db: DBSession,
) -> SOPResponse:
    sop = await SOPService(db).queue(user.id, payload)
    background.add_task(_process_sop_job, sop.id, payload.instructions)
    return SOPResponse.model_validate(sop)


@router.get("", response_model=list[SOPListItem])
async def list_sops(user: CurrentUser, db: DBSession) -> list[SOPListItem]:
    sops = await SOPService(db).list_for_owner(user.id)
    return [SOPListItem.model_validate(s) for s in sops]


@router.get("/{sop_id}", response_model=SOPResponse)
async def get_sop(sop_id: str, user: CurrentUser, db: DBSession) -> SOPResponse:
    sop = await SOPService(db).get_for_owner(sop_id, user.id)
    return SOPResponse.model_validate(sop)


@router.patch("/{sop_id}", response_model=SOPResponse)
async def update_sop(
    sop_id: str, payload: SOPUpdateRequest, user: CurrentUser, db: DBSession
) -> SOPResponse:
    sop = await SOPService(db).update(sop_id, user.id, payload)
    return SOPResponse.model_validate(sop)


@router.delete("/{sop_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_sop(sop_id: str, user: CurrentUser, db: DBSession) -> Response:
    await SOPService(db).delete(sop_id, user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{sop_id}/download")
async def download_sop(
    sop_id: str,
    fmt: str,
    user: CurrentUser,
    db: DBSession,
) -> Response:
    """Download an SOP as `md`, `docx`, or `pdf` (?fmt=...)."""
    if fmt not in ("md", "docx", "pdf"):
        raise HTTPException(status_code=400, detail="fmt must be one of: md, docx, pdf")
    sop = await SOPService(db).get_for_owner(sop_id, user.id)
    if not sop.markdown:
        raise HTTPException(status_code=409, detail="SOP has no content to export yet.")
    payload = exporter.render(fmt=fmt, title=sop.title, markdown_text=sop.markdown)
    filename = exporter.safe_filename(sop.title, fmt)
    return Response(
        content=payload,
        media_type=exporter.MIME[fmt],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{sop_id}/stream")
async def stream_refinement(sop_id: str, message: str, user: CurrentUser, db: DBSession):
    """Server-Sent Events: stream a refined SOP based on a user prompt."""
    sop = await SOPService(db).get_for_owner(sop_id, user.id)
    orchestrator = SOPOrchestrator()

    async def event_source():
        async for token in orchestrator.refine_stream(
            current_sop=sop.markdown or "", user_message=message
        ):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(event_source(), media_type="text/event-stream")
