"""Authentication endpoints.

This portal is restricted to a single provisioned credential. Self-service
registration is disabled by design — the only account is seeded from
environment variables at application startup.
"""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.deps import CurrentUser, DBSession
from app.schemas.auth import (
    AuthResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse)
async def login(payload: UserLoginRequest, db: DBSession) -> AuthResponse:
    return await AuthService(db).login(payload)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshTokenRequest, db: DBSession) -> TokenResponse:
    return await AuthService(db).refresh(payload.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user)
