"""
Project: AlphaQuant AI
File: backend/main.py
Description: FastAPI application factory and ASGI entrypoint.
Python Version: 3.11.9
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend.api.v1.router import api_router
from backend.cache.redis_client import redis_cache
from backend.database.base import Base
from backend.core.config import settings
from backend.core.exception_handlers import register_exception_handlers
from backend.core.logging import setup_logging
from backend.database.session import dispose_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle."""
    setup_logging(settings)
    logger.info(
        "Starting {app_name} {version}",
        app_name=settings.app_name,
        version=settings.app_version,
    )
    try:
        import backend.models.stock  # noqa: F401
        import backend.models.analysis  # noqa: F401
        import backend.models.portfolio  # noqa: F401
        import backend.models.research  # noqa: F401
        import backend.models.watchlist  # noqa: F401
        from backend.database.session import engine

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables auto-created")
    except Exception as exc:
        logger.warning(
            "Table creation failed: {error}",
            error=str(exc),
        )
    yield
    logger.info("Stopping {app_name}", app_name=settings.app_name)
    try:
        await redis_cache.close()
    except Exception:
        pass
    await dispose_engine()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        openapi_url=settings.openapi_url,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allowed_methods,
        allow_headers=settings.cors_allowed_headers,
    )
    register_exception_handlers(app, settings)
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
