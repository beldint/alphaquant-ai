"""
Project: AlphaQuant AI
File: backend/scheduler/jobs.py
Description: APScheduler jobs for trading, after-close, and nightly data refresh.
Python Version: 3.11.9
"""

from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from backend.core.config import settings
from backend.services.research_service import research_service


def create_scheduler() -> AsyncIOScheduler:
    """
    Create APScheduler instance.

    Returns:
        Configured async scheduler.
    """
    return AsyncIOScheduler(timezone=settings.scheduler_timezone)


def register_scheduler_jobs(scheduler: AsyncIOScheduler) -> None:
    """
    Register the final A-share data update strategy.

    Args:
        scheduler: Async scheduler instance.
    """
    scheduler.add_job(
        _refresh_trading_quotes_job,
        "cron",
        day_of_week="mon-fri",
        hour="9-11,13-14",
        second=0,
        minute=f"*/{max(settings.quote_refresh_interval_seconds // 60, 1)}",
        id="trading_realtime_quote_refresh",
        replace_existing=True,
    )
    scheduler.add_job(
        _refresh_after_close_job,
        "cron",
        day_of_week="mon-fri",
        hour=settings.after_close_refresh_hour,
        minute=settings.after_close_refresh_minute,
        id="after_close_research_refresh",
        replace_existing=True,
    )
    scheduler.add_job(
        _refresh_nightly_disclosures_job,
        "cron",
        day_of_week="mon-fri",
        hour=settings.nightly_refresh_hour,
        minute=settings.nightly_refresh_minute,
        id="nightly_disclosure_risk_refresh",
        replace_existing=True,
    )
    scheduler.add_job(
        _heartbeat_job,
        "interval",
        seconds=60,
        id="scheduler_heartbeat",
        replace_existing=True,
    )


async def _refresh_trading_quotes_job() -> None:
    """Refresh realtime prices for focused stocks during trading hours."""
    symbols = _research_symbols()
    result = await research_service.refresh_realtime_quotes(symbols)
    logger.info(
        "Trading quote refresh completed: requested={requested} refreshed={refreshed}",
        requested=len(symbols),
        refreshed=len(result),
    )


async def _refresh_after_close_job() -> None:
    """Run after-close Kline, technical indicator, and East Money refresh."""
    symbols = _research_symbols()
    result = await research_service.refresh_after_close(symbols, lookback_days=180)
    logger.info(
        "After-close refresh completed: requested={requested} refreshed={refreshed}",
        requested=len(symbols),
        refreshed=len(result),
    )


async def _refresh_nightly_disclosures_job() -> None:
    """Run nightly CNInfo announcement sync, report parsing, and risk scan."""
    symbols = _research_symbols()
    result = await research_service.refresh_nightly_disclosures(
        symbols,
        lookback_days=180,
    )
    logger.info(
        (
            "Nightly disclosure refresh completed: "
            "requested={requested} refreshed={refreshed}"
        ),
        requested=len(symbols),
        refreshed=len(result),
    )


async def _heartbeat_job() -> None:
    """Emit scheduler heartbeat for operational observability."""
    logger.debug("Scheduler heartbeat")


def _research_symbols() -> list[str]:
    """Return configured personal research symbols."""
    return list(settings.research_default_symbols)
