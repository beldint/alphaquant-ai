"""
Project: AlphaQuant AI
File: backend/models/portfolio.py
Description: Portfolio and holding ORM models.
Python Version: 3.11.9
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base, ReprMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Portfolio(UUIDPrimaryKeyMixin, TimestampMixin, ReprMixin, Base):
    """User investment portfolio."""

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    base_currency: Mapped[str] = mapped_column(String(16), nullable=False, default="CNY")
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_portfolio_user_name"),
        Index("ix_portfolio_user", "user_id"),
    )


class PortfolioHolding(UUIDPrimaryKeyMixin, TimestampMixin, ReprMixin, Base):
    """Current holding in a portfolio."""

    portfolio_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("portfolio.id"),
        nullable=False,
    )
    stock_id: Mapped[str] = mapped_column(String(36), ForeignKey("stock.id"), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(24, 4), nullable=False)
    average_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    market_value: Mapped[Decimal | None] = mapped_column(Numeric(24, 4), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "portfolio_id",
            "stock_id",
            name="uq_portfolio_holding_portfolio_stock",
        ),
        Index("ix_portfolio_holding_stock", "stock_id"),
    )

