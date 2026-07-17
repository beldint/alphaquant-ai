"""
Project: AlphaQuant AI
File: backend/scheduler/jobs.py
Description: APScheduler job registration for periodic market operations.
Python Version: 3.11.9
"""

from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from backend.core.config import settings


def create_scheduler() -> AsyncIOScheduler:
    """
    Create APScheduler instance.

    Returns:
        Configured async scheduler.
    """
    return AsyncIOScheduler(timezone=settings.scheduler_timezone)


def register_scheduler_jobs(scheduler: AsyncIOScheduler) -> None:
    """
    Register periodic scheduler jobs.

    Args:
        scheduler: Async scheduler instance.
    """
    scheduler.add_job(
        _heartbeat_job,
        "interval",
        seconds=max(settings.quote_refresh_interval_seconds, 5),
        id="scheduler_heartbeat",
        replace_existing=True,
    )


async def _heartbeat_job() -> None:
    """Emit scheduler heartbeat for operational observability."""
    logger.debug("Scheduler heartbeat")

