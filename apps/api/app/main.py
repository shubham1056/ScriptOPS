"""TranscribeOP — FastAPI application entrypoint."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.constants import API_V1_PREFIX, DOCS_URL, OPENAPI_URL, REDOC_URL
from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.seed import seed_portal_user
from app.middleware.rate_limit import register_rate_limiter
from app.middleware.request_context import RequestContextMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("startup", env=settings.APP_ENV, version=settings.APP_VERSION)
    # Auto-create tables in dev (use Alembic in prod)
    if not settings.is_production:
        await init_db()
    # Provision the single portal credential before serving any requests.
    await seed_portal_user()
    yield
    logger.info("shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url=DOCS_URL,
        redoc_url=REDOC_URL,
        openapi_url=OPENAPI_URL,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # Custom middleware (order matters — outermost first)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestContextMiddleware)

    # Rate limiting + exception handlers
    register_rate_limiter(app)
    register_exception_handlers(app)

    # Routes
    app.include_router(api_router, prefix=API_V1_PREFIX)

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": DOCS_URL,
            "api": API_V1_PREFIX,
        }

    return app


app = create_app()
