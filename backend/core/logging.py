"""
Project: AlphaQuant AI
File: backend/core/logging.py
Description: Loguru configuration for application and access logs.
Python Version: 3.11.9
"""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from backend.core.config import Settings


def setup_logging(settings: Settings) -> None:
    """
    Configure Loguru console and rotating file sinks.

    Args:
        settings: Loaded application settings.
    """
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.log_level.value,
        enqueue=settings.log_enqueue,
        backtrace=settings.log_backtrace,
        diagnose=settings.log_diagnose,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
    )
    logger.add(
        settings.log_file_path,
        level=settings.log_level.value,
        rotation=settings.log_rotation,
        retention=f"{settings.log_retention_days} days",
        compression=settings.log_compression,
        enqueue=settings.log_enqueue,
        backtrace=settings.log_backtrace,
        diagnose=settings.log_diagnose,
        encoding="utf-8",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
            "{process} | {thread} | {name}:{function}:{line} | {message}"
        ),
    )


def get_logger_context(**kwargs: str | int | float | bool | None) -> dict[str, object]:
    """
    Build a sanitized context dictionary for structured logging.

    Args:
        kwargs: Arbitrary scalar values to include in the log context.

    Returns:
        Dictionary containing only non-null context values.
    """
    return {key: value for key, value in kwargs.items() if value is not None}

