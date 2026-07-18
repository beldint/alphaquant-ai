"""
Project: AlphaQuant AI
File: backend/datasource/providers/http_client.py
Description: HTTP client factory hardened for local Windows runtime quirks.
Python Version: 3.11.9
"""

from __future__ import annotations

import os
from collections.abc import Mapping

import httpx


def build_async_client(
    *,
    timeout: float,
    headers: Mapping[str, str] | None = None,
    base_url: str | None = None,
) -> httpx.AsyncClient:
    """
    Build an HTTPX async client without inheriting fragile local env settings.

    Some Windows security tools set SSLKEYLOGFILE to a protected path. Python's
    ssl module reads that variable while creating the SSL context, so client
    construction can fail before any request is sent.

    Args:
        timeout: Request timeout in seconds.
        headers: Optional default headers.
        base_url: Optional base URL.

    Returns:
        Configured async HTTP client.
    """
    ssl_keylog_file = os.environ.pop("SSLKEYLOGFILE", None)
    try:
        return httpx.AsyncClient(
            base_url=(base_url or "").rstrip("/"),
            timeout=timeout,
            trust_env=False,
            headers=dict(headers or {}),
        )
    finally:
        if ssl_keylog_file is not None:
            os.environ["SSLKEYLOGFILE"] = ssl_keylog_file
