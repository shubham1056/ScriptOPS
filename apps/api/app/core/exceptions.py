"""Domain exceptions + global FastAPI exception handlers."""
from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------
class AppException(Exception):
    """Base application exception."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None, *, error_code: str | None = None) -> None:
        if message:
            self.message = message
        if error_code:
            self.error_code = error_code
        super().__init__(self.message)


class NotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"
    message = "Resource not found."


class ConflictError(AppException):
    status_code = status.HTTP_409_CONFLICT
    error_code = "CONFLICT"
    message = "Resource conflict."


class UnauthorizedError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "UNAUTHORIZED"
    message = "Authentication required."


class ForbiddenError(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "FORBIDDEN"
    message = "Insufficient permissions."


class ValidationError(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_ERROR"
    message = "Invalid input."


class AIServiceError(AppException):
    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "AI_SERVICE_ERROR"
    message = "AI service request failed."


class StorageError(AppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "STORAGE_ERROR"
    message = "Storage backend error."


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _error_response(status_code: int, error_code: str, message: str, details: object = None) -> JSONResponse:
    payload: dict[str, object] = {"error": {"code": error_code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details  # type: ignore[index]
    return JSONResponse(status_code=status_code, content=payload)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
def register_exception_handlers(app: FastAPI) -> None:
    """Attach centralized exception handlers."""

    @app.exception_handler(AppException)
    async def _app_exc(_: Request, exc: AppException) -> JSONResponse:
        logger.warning("app_exception", code=exc.error_code, message=exc.message)
        return _error_response(exc.status_code, exc.error_code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def _validation_exc(_: Request, exc: RequestValidationError) -> JSONResponse:
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "VALIDATION_ERROR",
            "Invalid request payload.",
            details=exc.errors(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_exc(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _error_response(exc.status_code, "HTTP_ERROR", str(exc.detail))

    @app.exception_handler(SQLAlchemyError)
    async def _db_exc(_: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.error("database_error", error=str(exc))
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "DATABASE_ERROR",
            "A database error occurred.",
        )

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", error=str(exc))
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_ERROR",
            "An unexpected error occurred.",
        )
