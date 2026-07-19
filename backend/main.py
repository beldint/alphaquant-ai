"""
Project: AlphaQuant AI
File: backend/main.py
Description: FastAPI application factory and ASGI entrypoint.
Python Version: 3.11.9
"""

from __future__ import annotations

import os
import tempfile

# Fix SSL keylog file permission issue caused by security software.
# The system environment variable SSLKEYLOGFILE points to a non-writable path,
# causing ALL HTTPS requests to fail with PermissionError.
_ssl_keylog = os.environ.get("SSLKEYLOGFILE")
if _ssl_keylog:
    try:
        # Test if we can write to the configured path
        open(_ssl_keylog, "a").close()
    except (OSError, PermissionError):
        # Redirect to a writable temp file or disable it
        writable_path = os.path.join(tempfile.gettempdir(), "ssl_keylog.txt")
        os.environ["SSLKEYLOGFILE"] = writable_path
        # Ensure the file is writable
        try:
            open(writable_path, "a").close()
        except (OSError, PermissionError):
            # If still fails, disable SSL key logging entirely
            os.environ.pop("SSLKEYLOGFILE", None)
del _ssl_keylog, writable_path

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

    # Serve built frontend static files for standalone deployments
    frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    if frontend_dist.is_dir():
        logger.info("Mounting frontend static files from {dir}", dir=str(frontend_dist))
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
    else:
        logger.info("No frontend dist found at {dir}; API-only mode", dir=str(frontend_dist))

    return app


app = create_app()
