"""Portal credential seeder.

Ensures the single configured portal account exists in the database. Runs on
application startup. If PORTAL_USER_EMAIL / PORTAL_USER_PASSWORD are missing,
startup aborts — the portal must not run without a known credential.
"""
from __future__ import annotations

from sqlalchemy import delete

from app.constants import UserRole
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository

logger = get_logger(__name__)


async def seed_portal_user() -> None:
    """Ensure exactly one portal user exists with the configured credentials."""
    email = settings.PORTAL_USER_EMAIL
    password = settings.PORTAL_USER_PASSWORD

    if not email or not password:
        raise RuntimeError(
            "PORTAL_USER_EMAIL and PORTAL_USER_PASSWORD must be set in the environment."
        )

    async with AsyncSessionLocal() as db:
        users = UserRepository(db)
        existing = await users.get_by_email(email)

        if existing is None:
            user = User(
                email=email,
                full_name=settings.PORTAL_USER_NAME,
                password_hash=hash_password(password),
                role=UserRole.ADMIN.value,
                is_active=True,
            )
            await users.add(user)
            logger.info("portal_user_created", email=email)
        else:
            updated = False
            if not verify_password(password, existing.password_hash):
                existing.password_hash = hash_password(password)
                updated = True
            if existing.full_name != settings.PORTAL_USER_NAME:
                existing.full_name = settings.PORTAL_USER_NAME
                updated = True
            if existing.role != UserRole.ADMIN.value:
                existing.role = UserRole.ADMIN.value
                updated = True
            if not existing.is_active:
                existing.is_active = True
                updated = True
            if updated:
                logger.info("portal_user_updated", email=email)

        # Purge any stale accounts — only the configured portal user may exist.
        await db.execute(delete(User).where(User.email != email))
        await db.commit()
