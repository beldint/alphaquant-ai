"""
Project: AlphaQuant AI
File: backend/core/exceptions.py
Description: Unified business and infrastructure exceptions for the backend.
Python Version: 3.11.9
"""

from __future__ import annotations

from enum import StrEnum
from http import HTTPStatus
from typing import Any


class ErrorCode(StrEnum):
    """Stable application error codes returned by API exception handlers."""

    BUSINESS_ERROR = "BUSINESS_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    STOCK_ERROR = "STOCK_ERROR"
    AI_ERROR = "AI_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    CACHE_ERROR = "CACHE_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    NOT_FOUND_ERROR = "NOT_FOUND_ERROR"
    CONFLICT_ERROR = "CONFLICT_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"


class AlphaQuantException(Exception):
    """Base exception carrying API-safe error metadata."""

    def __init__(
        self,
        message: str,
        *,
        code: ErrorCode,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """
        Initialize a structured AlphaQuant exception.

        Args:
            message: Human-readable error message safe for API responses.
            code: Stable machine-readable error code.
            status_code: HTTP status code used by exception handlers.
            details: Optional structured context for logs and API responses.
            cause: Optional original exception for exception chaining.
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = int(status_code)
        self.details = details or {}
        self.cause = cause

    def to_dict(self, *, include_details: bool = True) -> dict[str, Any]:
        """
        Convert the exception into the unified API response error payload.

        Args:
            include_details: Whether structured details should be included.

        Returns:
            Dictionary compatible with the project's unified response format.
        """
        payload: dict[str, Any] = {
            "code": self.code.value,
            "message": self.message,
        }
        if include_details and self.details:
            payload["details"] = self.details
        return payload


class BusinessException(AlphaQuantException):
    """Exception raised for domain rule violations and user-facing failures."""

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize a business exception."""
        super().__init__(
            message,
            code=ErrorCode.BUSINESS_ERROR,
            status_code=HTTPStatus.BAD_REQUEST,
            details=details,
            cause=cause,
        )


class DatabaseException(AlphaQuantException):
    """Exception raised for database access, transaction, and persistence errors."""

    def __init__(
        self,
        message: str = "Database operation failed",
        *,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize a database exception."""
        super().__init__(
            message,
            code=ErrorCode.DATABASE_ERROR,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            details=details,
            cause=cause,
        )


class StockException(AlphaQuantException):
    """Exception raised by stock market data providers and stock services."""

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        symbol: str | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize a stock data exception."""
        normalized_details = dict(details or {})
        if provider:
            normalized_details["provider"] = provider
        if symbol:
            normalized_details["symbol"] = symbol
        super().__init__(
            message,
            code=ErrorCode.STOCK_ERROR,
            status_code=HTTPStatus.BAD_GATEWAY,
            details=normalized_details,
            cause=cause,
        )


class AIException(AlphaQuantException):
    """Exception raised by AI providers and analysis orchestration services."""

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize an AI provider exception."""
        normalized_details = dict(details or {})
        if provider:
            normalized_details["provider"] = provider
        if model:
            normalized_details["model"] = model
        super().__init__(
            message,
            code=ErrorCode.AI_ERROR,
            status_code=HTTPStatus.BAD_GATEWAY,
            details=normalized_details,
            cause=cause,
        )


class NetworkException(AlphaQuantException):
    """Exception raised for outbound HTTP, DNS, timeout, and retry failures."""

    def __init__(
        self,
        message: str = "Network request failed",
        *,
        url: str | None = None,
        method: str | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize a network exception."""
        normalized_details = dict(details or {})
        if url:
            normalized_details["url"] = url
        if method:
            normalized_details["method"] = method.upper()
        super().__init__(
            message,
            code=ErrorCode.NETWORK_ERROR,
            status_code=HTTPStatus.BAD_GATEWAY,
            details=normalized_details,
            cause=cause,
        )


class ValidationException(AlphaQuantException):
    """Exception raised for request, command, and domain input validation errors."""

    def __init__(
        self,
        message: str = "Validation failed",
        *,
        field_errors: dict[str, str] | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize a validation exception."""
        normalized_details = dict(details or {})
        if field_errors:
            normalized_details["field_errors"] = field_errors
        super().__init__(
            message,
            code=ErrorCode.VALIDATION_ERROR,
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            details=normalized_details,
            cause=cause,
        )


class AuthenticationException(AlphaQuantException):
    """Exception raised when a user or service cannot be authenticated."""

    def __init__(
        self,
        message: str = "Authentication required",
        *,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize an authentication exception."""
        super().__init__(
            message,
            code=ErrorCode.AUTHENTICATION_ERROR,
            status_code=HTTPStatus.UNAUTHORIZED,
            details=details,
            cause=cause,
        )


class AuthorizationException(AlphaQuantException):
    """Exception raised when an authenticated principal lacks permissions."""

    def __init__(
        self,
        message: str = "Permission denied",
        *,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize an authorization exception."""
        super().__init__(
            message,
            code=ErrorCode.AUTHORIZATION_ERROR,
            status_code=HTTPStatus.FORBIDDEN,
            details=details,
            cause=cause,
        )


class CacheException(AlphaQuantException):
    """Exception raised for Redis cache read, write, serialization, and TTL errors."""

    def __init__(
        self,
        message: str = "Cache operation failed",
        *,
        key: str | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize a cache exception."""
        normalized_details = dict(details or {})
        if key:
            normalized_details["key"] = key
        super().__init__(
            message,
            code=ErrorCode.CACHE_ERROR,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            details=normalized_details,
            cause=cause,
        )


class RateLimitException(AlphaQuantException):
    """Exception raised when API, user, or provider rate limits are exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        *,
        retry_after_seconds: int | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize a rate limit exception."""
        normalized_details = dict(details or {})
        if retry_after_seconds is not None:
            normalized_details["retry_after_seconds"] = retry_after_seconds
        super().__init__(
            message,
            code=ErrorCode.RATE_LIMIT_ERROR,
            status_code=HTTPStatus.TOO_MANY_REQUESTS,
            details=normalized_details,
            cause=cause,
        )


class NotFoundException(AlphaQuantException):
    """Exception raised when a requested resource does not exist."""

    def __init__(
        self,
        message: str = "Resource not found",
        *,
        resource: str | None = None,
        identifier: str | int | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize a not-found exception."""
        normalized_details = dict(details or {})
        if resource:
            normalized_details["resource"] = resource
        if identifier is not None:
            normalized_details["identifier"] = identifier
        super().__init__(
            message,
            code=ErrorCode.NOT_FOUND_ERROR,
            status_code=HTTPStatus.NOT_FOUND,
            details=normalized_details,
            cause=cause,
        )


class ConflictException(AlphaQuantException):
    """Exception raised for duplicate resources and optimistic conflict failures."""

    def __init__(
        self,
        message: str = "Resource conflict",
        *,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize a conflict exception."""
        super().__init__(
            message,
            code=ErrorCode.CONFLICT_ERROR,
            status_code=HTTPStatus.CONFLICT,
            details=details,
            cause=cause,
        )


class ExternalServiceException(AlphaQuantException):
    """Exception raised when a third-party service returns an invalid response."""

    def __init__(
        self,
        message: str = "External service request failed",
        *,
        service: str | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize an external service exception."""
        normalized_details = dict(details or {})
        if service:
            normalized_details["service"] = service
        super().__init__(
            message,
            code=ErrorCode.EXTERNAL_SERVICE_ERROR,
            status_code=HTTPStatus.BAD_GATEWAY,
            details=normalized_details,
            cause=cause,
        )


class ConfigurationException(AlphaQuantException):
    """Exception raised for invalid runtime configuration."""

    def __init__(
        self,
        message: str = "Invalid application configuration",
        *,
        setting_name: str | None = None,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        """Initialize a configuration exception."""
        normalized_details = dict(details or {})
        if setting_name:
            normalized_details["setting_name"] = setting_name
        super().__init__(
            message,
            code=ErrorCode.CONFIGURATION_ERROR,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            details=normalized_details,
            cause=cause,
        )
