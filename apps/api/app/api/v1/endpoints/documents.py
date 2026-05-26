"""Document upload endpoints."""
from __future__ import annotations

from fastapi import APIRouter, File, Response, UploadFile, status

from app.api.v1.deps import CurrentUser, DBSession
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    user: CurrentUser,
    db: DBSession,
    file: UploadFile = File(...),
) -> DocumentResponse:
    doc = await DocumentService(db).upload(user.id, file)
    return DocumentResponse.model_validate(doc)


@router.get("", response_model=list[DocumentResponse])
async def list_documents(user: CurrentUser, db: DBSession) -> list[DocumentResponse]:
    docs = await DocumentService(db).list_for_owner(user.id)
    return [DocumentResponse.model_validate(d) for d in docs]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, user: CurrentUser, db: DBSession) -> DocumentResponse:
    doc = await DocumentService(db).get_for_owner(document_id, user.id)
    return DocumentResponse.model_validate(doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_document(document_id: str, user: CurrentUser, db: DBSession) -> Response:
    await DocumentService(db).delete(document_id, user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
