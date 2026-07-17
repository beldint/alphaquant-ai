"""
Project: AlphaQuant AI
File: backend/schemas/common.py
Description: Shared Pydantic schemas for API requests and responses.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ORMModel(BaseModel):
    """Base schema configured for SQLAlchemy ORM serialization."""

    model_config = ConfigDict(from_attributes=True)


class PaginationQuery(BaseModel):
    """Common pagination query parameters."""

    page: int = Field(default=1, ge=1, description="Page number starting from 1.")
    page_size: int = Field(default=20, ge=1, le=200, description="Page size.")

    @property
    def offset(self) -> int:
        """Return SQL offset computed from page and page size."""
        return (self.page - 1) * self.page_size


class DateRangeQuery(BaseModel):
    """Common date range query."""

    start_date: date | None = Field(default=None)
    end_date: date | None = Field(default=None)

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, value: date | None, info: object) -> date | None:
        """
        Validate that the end date is not earlier than the start date.

        Args:
            value: End date value.
            info: Pydantic validation info.

        Returns:
            Validated end date.
        """
        data = getattr(info, "data", {})
        start_date = data.get("start_date") if isinstance(data, dict) else None
        if value is not None and start_date is not None and value < start_date:
            raise ValueError("end_date must be greater than or equal to start_date")
        return value


class SortQuery(BaseModel):
    """Common sort query parameters."""

    sort_by: str = Field(default="created_at", min_length=1, max_length=64)
    sort_order: Literal["asc", "desc"] = Field(default="desc")

