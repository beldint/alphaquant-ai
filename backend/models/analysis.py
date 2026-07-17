"""
Project: AlphaQuant AI
File: backend/models/analysis.py
Description: AI stock analysis report ORM model.
Python Version: 3.11.9
"""

from __future__ import annotations

from sqlalchemy import ForeignKey, Index, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.database.base import Base, ReprMixin, TimestampMixin, UUIDPrimaryKeyMixin


class AIAnalysisReport(UUIDPrimaryKeyMixin, TimestampMixin, ReprMixin, Base):
    """Persisted AI stock analysis report with source data metadata."""

    user_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("user.id"),
        nullable=True,
    )
    stock_id: Mapped[str] = mapped_column(String(36), ForeignKey("stock.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    report_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    objective_data: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    technical_summary: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    risk_summary: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    data_timestamp: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        Index("ix_ai_analysis_stock_created", "stock_id", "created_at"),
        Index("ix_ai_analysis_user_created", "user_id", "created_at"),
    )

