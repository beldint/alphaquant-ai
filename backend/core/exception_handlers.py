"""
Project: AlphaQuant AI
File: backend/core/exception_handlers.py
Description: FastAPI exception handlers using unified response contracts.
Python Version: 3.11.9
"""

from __future__ import annotations

from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError as PydanticValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.core.config import Settings
from backend.core.exceptions import AlphaQuantException, ValidationException
from backend.core.responses import (
    build_error_response,
    build_unhandled_error_response,
)


def register_exception_handlers(app: FastAPI, settings: Settings) -> None:
    """
    Register all application exception handlers on a FastAPI app.

    Args:
        app: FastAPI application instance.
        settings: Loaded application settings.
    """

    @app.exception_handler(AlphaQuantException)
    async def alphaquant_exception_handler(
        request: Request,
        exc: AlphaQuantException,
    ) -> JSONResponse:
        """Handle structured application exceptions."""
        logger.warning(
            "Application exception: path={path} code={code} message={message} "
            "details={details}",
            path=request.url.path,
            code=exc.code.value,
            message=exc.message,
            details=exc.details,
        )
        response = build_error_response(
            exc,
            include_details=not settings.is_production,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=response.model_dump(mode="json"),
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle FastAPI request validation errors."""
        field_errors = _extract_validation_errors(exc.errors())
        validation_exception = ValidationException(
            "Request validation failed",
            field_errors=field_errors,
        )
        logger.warning(
            "Request validation failed: path={path} errors={errors}",
            path=request.url.path,
            errors=field_errors,
        )
        response = build_error_response(
            validation_exception,
            include_details=not settings.is_production,
        )
        return JSONResponse(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content=response.model_dump(mode="json"),
        )

    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_exception_handler(
        request: Request,
        exc: PydanticValidationError,
    ) -> JSONResponse:
        """Handle Pydantic validation errors raised inside services."""
        field_errors = _extract_validation_errors(exc.errors())
        validation_exception = ValidationException(
            "Data validation failed",
            field_errors=field_errors,
        )
        logger.warning(
            "Data validation failed: path={path} errors={errors}",
            path=request.url.path,
            errors=field_errors,
        )
        response = build_error_response(
            validation_exception,
            include_details=not settings.is_production,
        )
        return JSONResponse(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content=response.model_dump(mode="json"),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        """Handle framework HTTP exceptions."""
        logger.warning(
            "HTTP exception: path={path} status={status} detail={detail}",
            path=request.url.path,
            status=exc.status_code,
            detail=exc.detail,
        )
        response = build_unhandled_error_response(
            message=str(exc.detail),
            include_details=not settings.is_production,
            details={"status_code": exc.status_code},
        )
        response.code = str(exc.status_code)
        return JSONResponse(
            status_code=exc.status_code,
            content=response.model_dump(mode="json"),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unexpected exceptions without leaking internals in production."""
        logger.exception(
            "Unhandled exception: path={path} error={error}",
            path=request.url.path,
            error=str(exc),
        )
        response = build_unhandled_error_response(
            include_details=not settings.is_production,
            details={"error": str(exc)},
        )
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=response.model_dump(mode="json"),
        )


def _extract_validation_errors(errors: list[dict[str, Any]]) -> dict[str, str]:
    """
    Convert Pydantic validation errors into a compact field error map.

    Args:
        errors: Raw Pydantic error dictionaries.

    Returns:
        Mapping from dotted field path to validation message.
    """
    field_errors: dict[str, str] = {}
    for error in errors:
        location = error.get("loc", ())
        field_name = ".".join(str(item) for item in location)
        message = str(error.get("msg", "Invalid value"))
        field_errors[field_name or "request"] = message
    return field_errors

