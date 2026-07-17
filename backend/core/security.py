"""
Project: AlphaQuant AI
File: backend/core/security.py
Description: Password hashing and JWT token utilities.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.core.config import settings
from backend.core.exceptions import AuthenticationException


password_context = CryptContext(
    schemes=[settings.password_hash_algorithm],
    deprecated="auto",
    bcrypt__rounds=settings.password_bcrypt_rounds,
)


def hash_password(password: str) -> str:
    """
    Hash a plaintext password.

    Args:
        password: Plaintext password.

    Returns:
        Password hash.
    """
    return str(password_context.hash(password))


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a stored hash.

    Args:
        password: Plaintext password.
        hashed_password: Stored password hash.

    Returns:
        True when password matches.
    """
    return bool(password_context.verify(password, hashed_password))


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """
    Create a signed access JWT.

    Args:
        subject: Token subject, usually the user id.
        extra_claims: Optional additional claims.

    Returns:
        Encoded JWT.
    """
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    return _create_token(subject, expires_delta, "access", extra_claims)


def create_refresh_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """
    Create a signed refresh JWT.

    Args:
        subject: Token subject, usually the user id.
        extra_claims: Optional additional claims.

    Returns:
        Encoded JWT.
    """
    expires_delta = timedelta(minutes=settings.refresh_token_expire_minutes)
    return _create_token(subject, expires_delta, "refresh", extra_claims)


def decode_token(token: str, *, expected_type: str | None = None) -> dict[str, Any]:
    """
    Decode and validate a JWT.

    Args:
        token: Encoded JWT.
        expected_type: Optional expected token type.

    Returns:
        Token claims.

    Raises:
        AuthenticationException: If token validation fails.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise AuthenticationException("Invalid authentication token", cause=exc) from exc

    subject = payload.get("sub")
    token_type = payload.get("type")
    if not isinstance(subject, str) or not subject:
        raise AuthenticationException("Invalid token subject")
    if expected_type is not None and token_type != expected_type:
        raise AuthenticationException("Invalid token type")
    return dict(payload)


def _create_token(
    subject: str,
    expires_delta: timedelta,
    token_type: str,
    extra_claims: dict[str, Any] | None,
) -> str:
    """
    Create a signed JWT with shared claims.

    Args:
        subject: Token subject.
        expires_delta: Token validity window.
        token_type: Token type claim.
        extra_claims: Optional additional claims.

    Returns:
        Encoded JWT.
    """
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return str(
        jwt.encode(
            payload,
            settings.jwt_secret_key.get_secret_value(),
            algorithm=settings.jwt_algorithm,
        ),
    )

