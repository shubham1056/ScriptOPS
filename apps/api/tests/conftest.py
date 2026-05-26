"""Pytest config — set test env vars before importing app."""
import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-pytest-must-be-at-least-32-chars")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("APP_ENV", "development")
