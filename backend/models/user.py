"""
Project: AlphaQuant AI
File: backend/models/user.py
Description: User, role, and permission ORM models for RBAC.
Python Version: 3.11.9
"""

from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Index, String, Table, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, ReprMixin, TimestampMixin, UUIDPrimaryKeyMixin


user_role_table = Table(
    "user_role",
    Base.metadata,
    Column("user_id", String(36), ForeignKey("user.id"), primary_key=True),
    Column("role_id", String(36), ForeignKey("role.id"), primary_key=True),
)

role_permission_table = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", String(36), ForeignKey("role.id"), primary_key=True),
    Column(
        "permission_id",
        String(36),
        ForeignKey("permission.id"),
        primary_key=True,
    ),
)


class User(UUIDPrimaryKeyMixin, TimestampMixin, ReprMixin, Base):
    """Application user account model."""

    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    roles: Mapped[list[Role]] = relationship(
        secondary=user_role_table,
        back_populates="users",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_user_username", "username"),
        Index("ix_user_email", "email"),
    )


class Role(UUIDPrimaryKeyMixin, TimestampMixin, ReprMixin, Base):
    """RBAC role model."""

    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    users: Mapped[list[User]] = relationship(
        secondary=user_role_table,
        back_populates="roles",
        lazy="selectin",
    )
    permissions: Mapped[list[Permission]] = relationship(
        secondary=role_permission_table,
        back_populates="roles",
        lazy="selectin",
    )


class Permission(UUIDPrimaryKeyMixin, TimestampMixin, ReprMixin, Base):
    """RBAC permission model."""

    code: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    resource: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)

    roles: Mapped[list[Role]] = relationship(
        secondary=role_permission_table,
        back_populates="permissions",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("resource", "action", name="uq_permission_resource_action"),
    )
