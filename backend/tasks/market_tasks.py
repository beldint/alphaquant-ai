"""
Project: AlphaQuant AI
File: backend/tasks/market_tasks.py
Description: Celery tasks for market data refresh.
Python Version: 3.11.9
"""

from __future__ import annotations

import asyncio

from loguru import logger

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
    logger.info("Refreshing quote: market={market} symbol={symbol}", market=market, symbol=symbol)
    quote = asyncio.run(stock_service.get_realtime_quote(symbol, market))  # type: ignore[arg-type]
    return quote.model_dump(mode="json")

