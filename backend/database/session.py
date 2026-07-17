"""
Project: AlphaQuant AI
File: backend/database/session.py
Description: Async SQLAlchemy engine, session factory, and transaction helpers.
Python Version: 3.11.9
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from loguru import logger
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.core.config import settings
from backend.core.exceptions import DatabaseException


engine: AsyncEngine = create_async_engine(
    settings.sqlalchemy_database_url,
    echo=settings.database_echo,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout_seconds,
    pool_recycle=settings.database_pool_recycle_seconds,
    poolclass=None,
    connect_args={"check_same_thread": False, "uri": True},
)

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an async database session for FastAPI dependencies.

    Yields:
        Async SQLAlchemy session.

    Raises:
        DatabaseException: If session lifecycle management fails.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except SQLAlchemyError as exc:
            await session.rollback()
            logger.exception("Database session failed: {error}", error=str(exc))
            raise DatabaseException(cause=exc) from exc
        finally:
            await session.close()


@asynccontextmanager
async def transaction() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async transactional session context.

    Yields:
        Async SQLAlchemy session with commit or rollback behavior.

    Raises:
        DatabaseException: If commit, rollback, or SQL execution fails.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.exception("Database transaction failed: {error}", error=str(exc))
            raise DatabaseException(cause=exc) from exc
        finally:
            await session.close()


async def check_database_health() -> bool:
    """
    Check whether the configured database is reachable.

    Returns:
        True when a simple query succeeds, otherwise False.
    """
    try:
        async with AsyncSessionFactory() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Database health check failed: {error}", error=str(exc))
        return False


async def dispose_engine() -> None:
    """Dispose database engine connections during application shutdown."""
    await engine.dispose()

