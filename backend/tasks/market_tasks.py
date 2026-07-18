"""
Project: AlphaQuant AI
File: backend/tasks/market_tasks.py
Description: Celery tasks for market data refresh.
Python Version: 3.11.9
"""

from __future__ import annotations

import asyncio

from loguru import logger

from backend.services.research_service import research_service
from backend.services.stock_service import stock_service
from backend.tasks.celery_app import celery_app


@celery_app.task(name="market.refresh_quote")
def refresh_quote(symbol: str, market: str = "A") -> dict[str, object]:
    """
    Refresh a stock quote cache entry.

    Args:
        symbol: Stock symbol.
        market: Market identifier.

    Returns:
        Refreshed quote payload.
    """
    logger.info(
        "Refreshing quote: market={market} symbol={symbol}",
        market=market,
        symbol=symbol,
    )
    quote = asyncio.run(stock_service.get_realtime_quote(symbol, market))  # type: ignore[arg-type]
    return quote.model_dump(mode="json")


@celery_app.task(name="market.refresh_realtime_quotes")
def refresh_realtime_quotes(
    symbols: list[str],
    market: str = "A",
) -> list[dict[str, object]]:
    """
    Refresh focused stock prices during trading hours.

    Args:
        symbols: Focused stock symbols.
        market: Market identifier.

    Returns:
        Refreshed quote payloads.
    """
    result = asyncio.run(
        research_service.refresh_realtime_quotes(
            symbols,
            market=market,  # type: ignore[arg-type]
        ),
    )
    return result


@celery_app.task(name="market.refresh_research")
def refresh_research(
    symbol: str,
    market: str = "A",
    lookback_days: int = 180,
) -> dict[str, object]:
    """
    Refresh full A-share research data and scoring snapshot.

    Args:
        symbol: Stock symbol.
        market: Market identifier.
        lookback_days: Kline lookback window.

    Returns:
        Refresh payload.
    """
    logger.info(
        "Refreshing research data: market={market} symbol={symbol}",
        market=market,
        symbol=symbol,
    )
    result = asyncio.run(
        research_service.refresh_stock(
            symbol,
            market=market,  # type: ignore[arg-type]
            lookback_days=lookback_days,
        ),
    )
    return result.model_dump(mode="json")


@celery_app.task(name="market.refresh_after_close")
def refresh_after_close(
    symbols: list[str],
    market: str = "A",
    lookback_days: int = 180,
) -> list[dict[str, object]]:
    """
    Refresh full-market Kline, technical indicators, and East Money data after close.

    Args:
        symbols: Stock symbols to refresh.
        market: Market identifier.
        lookback_days: Kline lookback window.

    Returns:
        Refresh result payloads.
    """
    result = asyncio.run(
        research_service.refresh_after_close(
            symbols,
            market=market,  # type: ignore[arg-type]
            lookback_days=lookback_days,
        ),
    )
    return [item.model_dump(mode="json") for item in result]


@celery_app.task(name="market.refresh_nightly_disclosures")
def refresh_nightly_disclosures(
    symbols: list[str],
    market: str = "A",
    lookback_days: int = 180,
) -> list[dict[str, object]]:
    """
    Refresh CNInfo announcements, financial reports, and risk scan at night.

    Args:
        symbols: Stock symbols to refresh.
        market: Market identifier.
        lookback_days: Kline lookback window.

    Returns:
        Refresh result payloads.
    """
    result = asyncio.run(
        research_service.refresh_nightly_disclosures(
            symbols,
            market=market,  # type: ignore[arg-type]
            lookback_days=lookback_days,
        ),
    )
    return [item.model_dump(mode="json") for item in result]
