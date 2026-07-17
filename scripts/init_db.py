"""
Project: AlphaQuant AI
File: scripts/init_db.py
Description: Create database tables from ORM models.
Python Version: 3.11.9
"""
from __future__ import annotations
import asyncio
from loguru import logger
from sqlalchemy import text
from backend.core.config import settings
from backend.database.base import Base
from backend.database.session import engine
import backend.models.stock  # noqa: F401
import backend.models.user  # noqa: F401
import backend.models.analysis  # noqa: F401
import backend.models.portfolio  # noqa: F401
import backend.models.watchlist  # noqa: F401

async def init_database() -> None:
    logger.info("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())
