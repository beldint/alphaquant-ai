"""
Project: AlphaQuant AI
File: backend/schemas/auth.py
Description: Authentication and authorization request/response schemas.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import datetime

from pydantic import EmailStr, Field

from backend.schemas.common import ORMModel


class UserCreateRequest(ORMModel):
    """Request schema for creating a user."""

    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=128)


class UserLoginRequest(ORMModel):
    """Request schema for user login."""

    username_or_email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(ORMModel):
    """JWT token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(ORMModel):
    """Public user response schema."""

    id: str
    username: str
    email: EmailStr
    full_name: str | None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

