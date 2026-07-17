"""
Project: AlphaQuant AI
File: backend/models/watchlist.py
Description: User watchlist ORM models.
Python Version: 3.11.9
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base, ReprMixin, TimestampMixin, UUIDPrimaryKeyMixin


class WatchlistItem(UUIDPrimaryKeyMixin, TimestampMixin, ReprMixin, Base):
    """User self-selected stock item."""

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("user.id"), nullable=False)
    stock_id: Mapped[str] = mapped_column(String(36), ForeignKey("stock.id"), nullable=False)
    group_name: Mapped[str] = mapped_column(String(64), nullable=False, default="default")
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "stock_id", name="uq_watchlist_user_stock"),
        Index("ix_watchlist_user_group", "user_id", "group_name"),
    )

