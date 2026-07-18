"""
Project: AlphaQuant AI
File: backend/models/research.py
Description: Core A-share research data tables for personal AI analysis.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import JSON, Date, DateTime, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base, ReprMixin, TimestampMixin, UUIDPrimaryKeyMixin


class StockPrice(UUIDPrimaryKeyMixin, TimestampMixin, ReprMixin, Base):
    """Canonical daily market data table: stock_price."""

    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    market: Mapped[str] = mapped_column(String(16), nullable=False, default="A")
    trade_date: Mapped[date] = mapped_column(Date, nullable=False)
    open_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    high_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    low_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    close_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    volume: Mapped[Decimal] = mapped_column(Numeric(24, 4), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(24, 4), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)

    __table_args__ = (
        Index("ix_stock_price_symbol_date", "symbol", "trade_date", unique=True),
        Index("ix_stock_price_market_date", "market", "trade_date"),
    )


class FinancialReport(UUIDPrimaryKeyMixin, TimestampMixin, ReprMixin, Base):
    """Canonical financial report table: financial_report."""

    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    market: Mapped[str] = mapped_column(String(16), nullable=False, default="A")
    report_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    revenue: Mapped[Decimal | None] = mapped_column(Numeric(24, 4), nullable=True)
    revenue_growth: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4), nullable=True
    )
    net_profit: Mapped[Decimal | None] = mapped_column(Numeric(24, 4), nullable=True)
    deducted_net_profit: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 4),
        nullable=True,
    )
    gross_margin: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    net_margin: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    roe: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    debt_ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    current_ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    quick_ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    cash: Mapped[Decimal | None] = mapped_column(Numeric(24, 4), nullable=True)
    interest_debt: Mapped[Decimal | None] = mapped_column(Numeric(24, 4), nullable=True)
    operating_cashflow: Mapped[Decimal | None] = mapped_column(
        Numeric(24, 4),
        nullable=True,
    )
    pe_ttm: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    pb: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    peg: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    dividend_yield: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 4), nullable=True
    )
    market_cap: Mapped[Decimal | None] = mapped_column(Numeric(24, 4), nullable=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="eastmoney")
    raw_data: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_financial_report_symbol_date", "symbol", "report_date", unique=True),
        Index("ix_financial_report_updated", "updated_at"),
    )


class CompanyRisk(UUIDPrimaryKeyMixin, TimestampMixin, ReprMixin, Base):
    """Canonical company risk table: company_risk."""

    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    market: Mapped[str] = mapped_column(String(16), nullable=False, default="A")
    risk_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default="medium")
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="cninfo")
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    raw_data: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_company_risk_symbol_published", "symbol", "published_at"),
        Index("ix_company_risk_type", "risk_type"),
    )


class StockScore(UUIDPrimaryKeyMixin, TimestampMixin, ReprMixin, Base):
    """Canonical stock score table: stock_score."""

    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    market: Mapped[str] = mapped_column(String(16), nullable=False, default="A")
    score_date: Mapped[date] = mapped_column(Date, nullable=False)
    fundamental_score: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    solvency_score: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    technical_score: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    valuation_score: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    risk_score: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    total_score: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    rating: Mapped[str] = mapped_column(String(32), nullable=False)
    strengths: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    risks: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    suggestion: Mapped[str] = mapped_column(Text, nullable=False)
    raw_breakdown: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)

    __table_args__ = (
        Index("ix_stock_score_symbol_date", "symbol", "score_date", unique=True),
        Index("ix_stock_score_total", "total_score"),
    )
