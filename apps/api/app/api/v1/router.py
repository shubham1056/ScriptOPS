"""Compose all v1 routers."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import auth, conversations, documents, health, sops

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(sops.router)
api_router.include_router(conversations.router)
