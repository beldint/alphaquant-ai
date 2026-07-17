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
from backend.core.config import settings
from backend.core.exception_handlers import register_exception_handlers
from backend.core.logging import setup_logging
from backend.database.session import dispose_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application startup and shutdown lifecycle.

    Args:
        app: FastAPI application instance.

    Yields:
        None during application runtime.
    """
    setup_logging(settings)
    logger.info("Starting {app_name} {version}", app_name=settings.app_name, version=settings.app_version)
    yield
    logger.info("Stopping {app_name}", app_name=settings.app_name)
    try:
        await redis_cache.close()
    except:
        pass
    await dispose_engine()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI app.
    """
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

