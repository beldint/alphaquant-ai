"""
Project: AlphaQuant AI
File: backend/database/base.py
Description: SQLAlchemy declarative base and reusable ORM mixins.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, MetaData, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Generate a snake_case table name from the model class name.

        Returns:
            SQL table name.
        """
        name = cls.__name__
        chars: list[str] = []
        for index, char in enumerate(name):
            if char.isupper() and index > 0:
                chars.append("_")
            chars.append(char.lower())
        return "".join(chars)


class UUIDPrimaryKeyMixin:
    """Mixin that provides a string UUID primary key."""

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        comment="Primary key UUID.",
    )


class TimestampMixin:
    """Mixin that provides created and updated timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp.",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Record update timestamp.",
    )


class ReprMixin:
    """Mixin that provides a compact debug representation for ORM models."""

    def __repr__(self) -> str:
        """
        Return a concise representation including the primary key when available.

        Returns:
            Debug-friendly representation string.
        """
        identifier = getattr(self, "id", None)
        return f"{self.__class__.__name__}(id={identifier!r})"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert loaded column values into a dictionary.

        Returns:
            Mapping of column names to current instance values.
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

