"""Authentication service.

The portal is locked to a single provisioned credential. Login only succeeds
for the configured PORTAL_USER_EMAIL — anything else is rejected with the
same generic error to avoid leaking which accounts exist.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import ACCESS_TOKEN_SUBJECT, REFRESH_TOKEN_SUBJECT
from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AuthResponse,
    TokenResponse,
    UserLoginRequest,
    UserResponse,
)


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)

    async def login(self, payload: UserLoginRequest) -> AuthResponse:
        email = payload.email.lower()

        # Hard gate: only the configured portal account may sign in.
        if email != settings.PORTAL_USER_EMAIL.lower():
            raise UnauthorizedError("Invalid email or password.")

        user = await self.users.get_by_email(email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password.")
        if not user.is_active:
            raise UnauthorizedError("Account disabled.")
        return self._build_response(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token, expected_type=REFRESH_TOKEN_SUBJECT)
        user = await self.users.get(payload["sub"])
        if not user or not user.is_active:
            raise UnauthorizedError("Invalid refresh token.")
        if user.email.lower() != settings.PORTAL_USER_EMAIL.lower():
            raise UnauthorizedError("Invalid refresh token.")
        return self._tokens_for(user)

    def _tokens_for(self, user: User) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(user.id, extra_claims={"role": user.role}),
            refresh_token=create_refresh_token(user.id),
            token_type=ACCESS_TOKEN_SUBJECT,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def _build_response(self, user: User) -> AuthResponse:
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=self._tokens_for(user),
        )
