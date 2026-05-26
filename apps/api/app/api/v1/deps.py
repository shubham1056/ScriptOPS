"""Shared FastAPI dependencies (DI)."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import ACCESS_TOKEN_SUBJECT, UserRole
from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.models.user import User
from app.repositories.user_repository import UserRepository

DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DBSession,
    authorization: str | None = Header(default=None),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing bearer token.")
    token = authorization.split(" ", 1)[1].strip()
    payload = decode_token(token, expected_type=ACCESS_TOKEN_SUBJECT)
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Malformed token.")
    user = await UserRepository(db).get(user_id)
    if not user or not user.is_active:
        raise UnauthorizedError("Account inactive.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*allowed: UserRole):
    async def _checker(user: CurrentUser) -> User:
        if user.role not in {r.value for r in allowed}:
            raise ForbiddenError("Insufficient role.")
        return user

    return _checker
