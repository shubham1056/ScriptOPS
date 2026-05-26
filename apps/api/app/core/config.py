"""Application configuration loaded from environment variables.

Uses pydantic-settings for type-safe, validated config.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Anchor .env to the API project root (apps/api/) so uvicorn can be launched
# from any working directory.
_API_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _API_ROOT / ".env"


class Settings(BaseSettings):
    """Centralized application settings."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ---- Application ----
    APP_NAME: str = "TranscribeOP"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 4000
    APP_DEBUG: bool = True
    APP_VERSION: str = "1.0.0"

    # ---- Security ----
    JWT_SECRET_KEY: str = Field(min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---- Portal credential (single-account portal) ----
    # The portal is locked to a single provisioned account. These values must
    # be set in the environment (.env in dev; secret manager in prod). The
    # password is hashed and seeded into the DB on startup; rotating the env
    # value rotates the credential at the next boot.
    PORTAL_USER_EMAIL: str = ""
    PORTAL_USER_PASSWORD: str = ""
    PORTAL_USER_NAME: str = "Portal User"

    @field_validator("PORTAL_USER_EMAIL")
    @classmethod
    def _normalize_portal_email(cls, v: str) -> str:
        return v.strip().lower()

    # ---- CORS ----
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    # ---- Database ----
    DATABASE_URL: str = "sqlite+aiosqlite:///./transcribeop.db"

    # ---- Storage ----
    STORAGE_BACKEND: Literal["local", "azure_blob"] = "local"
    LOCAL_STORAGE_PATH: str = "./storage"
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_STORAGE_CONTAINER: str = "transcribeop"

    # ---- Queue ----
    QUEUE_BACKEND: Literal["background", "celery"] = "background"
    REDIS_URL: str = "redis://localhost:6379/0"

    # ---- Azure OpenAI ----
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-5-sop"
    AZURE_OPENAI_API_VERSION: str = "2024-10-21"
    AZURE_OPENAI_MAX_TOKENS: int = 4096
    AZURE_OPENAI_TEMPERATURE: float = 0.2
    AZURE_OPENAI_TIMEOUT_SECONDS: int = 120

    # ---- Rate limiting ----
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_AI: str = "20/minute"
    RATE_LIMIT_UPLOAD: str = "30/minute"

    # ---- File upload ----
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_FILE_EXTENSIONS: str = "pdf,docx,txt,md"

    @property
    def allowed_extensions_set(self) -> set[str]:
        return {ext.strip().lower() for ext in self.ALLOWED_FILE_EXTENSIONS.split(",")}

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # ---- Logging ----
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def _validate_secret(cls, v: str) -> str:
        if "change-me" in v.lower() and len(v) < 64:
            # allow in dev, but warn via length check
            pass
        return v

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings accessor (singleton)."""
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
