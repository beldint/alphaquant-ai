"""
Project: AlphaQuant AI
File: backend/models/stock.py
Description: Stock market data ORM models.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base, ReprMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Stock(UUIDPrimaryKeyMixin, TimestampMixin, ReprMixin, Base):
    """Stock security master data."""

    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    market: Mapped[str] = mapped_column(String(16), nullable=False)
    exchange: Mapped[str] = mapped_column(String(32), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(128), nullable=True)
    listing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(String(16), nullable=False, default="CNY")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    __table_args__ = (
        Index("ix_stock_symbol_market", "symbol", "market", unique=True),
        Index("ix_stock_name", "name"),
        Index("ix_stock_industry", "industry"),
    )


class DailyKline(UUIDPrimaryKeyMixin, TimestampMixin, ReprMixin, Base):
    """Daily OHLCV market data for a stock."""

    stock_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("stock.id"),
        nullable=False,
    )
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    open_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    high_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    low_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    close_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    pre_close: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    volume: Mapped[Decimal] = mapped_column(Numeric(24, 4), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(24, 4), nullable=False)
    turnover_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)

    __table_args__ = (
        Index("ix_daily_kline_stock_date", "stock_id", "trade_date", unique=True),
        Index("ix_daily_kline_trade_date", "trade_date"),
    )


class StockNews(UUIDPrimaryKeyMixin, TimestampMixin, ReprMixin, Base):
    """News item related to a stock or market topic."""

    stock_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("stock.id"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    sentiment: Mapped[str | None] = mapped_column(String(32), nullable=True)

    __table_args__ = (
        Index("ix_stock_news_stock_published", "stock_id", "published_at"),
        Index("ix_stock_news_url", "url", unique=True),
    )


class StockAnnouncement(UUIDPrimaryKeyMixin, TimestampMixin, ReprMixin, Base):
    """Listed company announcement metadata."""

    stock_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("stock.id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        Index("ix_stock_announcement_stock_published", "stock_id", "published_at"),
        Index("ix_stock_announcement_url", "url", unique=True),
    )

