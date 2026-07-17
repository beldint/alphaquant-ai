"""
Project: AlphaQuant AI
File: backend/core/responses.py
Description: Unified API response models and helpers for FastAPI endpoints.
Python Version: 3.11.9
"""

from __future__ import annotations

from http import HTTPStatus
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from backend.core.exceptions import AlphaQuantException


DataT = TypeVar("DataT")


class ResponseCode:
    """Standard numeric response codes used by successful API responses."""

    SUCCESS: int = 0


class APIResponse(BaseModel, Generic[DataT]):
    """Generic API response model following the project response contract."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "code": 0,
                "message": "success",
                "data": {},
            },
        },
    )

    code: int | str = Field(description="Business response code.")
    message: str = Field(description="Human-readable response message.")
    data: DataT | None = Field(default=None, description="Response payload.")


class ErrorResponse(BaseModel):
    """API response model for structured errors."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "BUSINESS_ERROR",
                "message": "Invalid request",
                "data": {
                    "details": {
                        "reason": "The requested operation violates business rules.",
                    },
                },
            },
        },
    )

    code: str = Field(description="Stable machine-readable error code.")
    message: str = Field(description="API-safe error message.")
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured error metadata.",
    )


class PaginationMeta(BaseModel):
    """Pagination metadata returned by list endpoints."""

    page: int = Field(ge=1, description="Current page number.")
    page_size: int = Field(ge=1, description="Number of records per page.")
    total: int = Field(ge=0, description="Total number of records.")
    total_pages: int = Field(ge=0, description="Total number of pages.")
    has_next: bool = Field(description="Whether a next page exists.")
    has_previous: bool = Field(description="Whether a previous page exists.")


class PageResponse(BaseModel, Generic[DataT]):
    """Paginated response payload used by collection endpoints."""

    items: list[DataT] = Field(default_factory=list, description="Current page items.")
    meta: PaginationMeta = Field(description="Pagination metadata.")


def build_success_response(
    data: DataT | None = None,
    *,
    message: str = "success",
) -> APIResponse[DataT]:
    """
    Build a successful API response.

    Args:
        data: Response payload.
        message: Human-readable success message.

    Returns:
        Unified successful API response object.
    """
    return APIResponse[DataT](
        code=ResponseCode.SUCCESS,
        message=message,
        data=data,
    )


def build_error_response(
    exception: AlphaQuantException,
    *,
    include_details: bool = True,
) -> ErrorResponse:
    """
    Build an error response from a structured application exception.

    Args:
        exception: Structured AlphaQuant exception.
        include_details: Whether exception details should be included.

    Returns:
        Unified error response object.
    """
    details = exception.details if include_details else {}
    return ErrorResponse(
        code=exception.code.value,
        message=exception.message,
        data={"details": details} if details else {},
    )


def build_unhandled_error_response(
    *,
    message: str = "Internal server error",
    include_details: bool = False,
    details: dict[str, Any] | None = None,
) -> ErrorResponse:
    """
    Build a safe response for unexpected exceptions.

    Args:
        message: API-safe error message.
        include_details: Whether debug details should be exposed.
        details: Optional diagnostic details intended for non-production environments.

    Returns:
        Unified error response object.
    """
    response_data = {"details": details or {}} if include_details and details else {}
    return ErrorResponse(
        code=str(HTTPStatus.INTERNAL_SERVER_ERROR.value),
        message=message,
        data=response_data,
    )


def build_page_response(
    items: list[DataT],
    *,
    page: int,
    page_size: int,
    total: int,
) -> PageResponse[DataT]:
    """
    Build a paginated response payload.

    Args:
        items: Current page records.
        page: Current page number, starting from 1.
        page_size: Number of records per page.
        total: Total number of matched records.

    Returns:
        Paginated payload with computed metadata.

    Raises:
        ValueError: If pagination parameters are invalid.
    """
    if page < 1:
        raise ValueError("page must be greater than or equal to 1")
    if page_size < 1:
        raise ValueError("page_size must be greater than or equal to 1")
    if total < 0:
        raise ValueError("total must be greater than or equal to 0")

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1 and total_pages > 0,
    )
    return PageResponse[DataT](items=items, meta=meta)
