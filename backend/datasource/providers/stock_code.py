"""
Project: AlphaQuant AI
File: backend/datasource/providers/stock_code.py
Description: A-share stock code normalization helpers for public market APIs.
Python Version: 3.11.9
"""

from __future__ import annotations

from backend.core.exceptions import StockException


def normalize_symbol(symbol: str) -> str:
    """
    Normalize a user-provided stock symbol to a plain six-digit A-share code,
    stripping optional exchange suffixes (.SS, .SZ, .BJ) or prefixes (sh, sz, bj).

    Args:
        symbol: Stock code, optionally prefixed with exchange text.

    Returns:
        Six-digit stock symbol.
    """
    value = symbol.strip().lower()
    # Strip .ss, .sz, .bj, .hk suffixes (e.g. "600519.ss" -> "600519")
    for suffix in (".ss", ".sz", ".bj", ".hk"):
        if value.endswith(suffix):
            value = value[:-len(suffix)]
            break
    for prefix in ("sh", "sz", "bj"):
        if value.startswith(prefix):
            value = value[2:]
            break
    if not value.isdigit() or len(value) != 6:
        raise StockException("Invalid A-share symbol", symbol=symbol)
    return value


def infer_exchange(symbol: str) -> str:
    """
    Infer the exchange code for a normalized A-share symbol.

    Args:
        symbol: Six-digit stock symbol.

    Returns:
        SSE, SZSE, BSE, or UNKNOWN.
    """
    code = normalize_symbol(symbol)
    # Known SSE/CSI index codes in 000xxx range (belong to SSE, not SZSE)
    SSE_INDEX_CODES_000 = {
        "000016",  # SSE 50
        "000300",  # CSI 300
        "000688",  # STAR 50 / KeChuang50
        "000905",  # CSI 500
    }
    if code in SSE_INDEX_CODES_000:
        return "SSE"
    if code.startswith(("5", "6", "9")):
        return "SSE"
    if code.startswith(("0", "2", "3")):
        return "SZSE"
    if code.startswith(("4", "8")):
        return "BSE"
    return "UNKNOWN"


def exchange_prefix(symbol: str) -> str:
    """
    Return the lower-case exchange prefix used by Sina and Tencent.

    Args:
        symbol: Six-digit stock symbol.

    Returns:
        sh, sz, or bj.
    """
    exchange = infer_exchange(symbol)
    if exchange == "SSE":
        return "sh"
    if exchange == "SZSE":
        return "sz"
    if exchange == "BSE":
        return "bj"
    raise StockException("Cannot infer exchange for symbol", symbol=symbol)


def prefixed_symbol(symbol: str) -> str:
    """
    Return the Sina/Tencent style symbol, such as sh600519.

    Args:
        symbol: Six-digit stock symbol.

    Returns:
        Exchange-prefixed symbol.
    """
    code = normalize_symbol(symbol)
    return f"{exchange_prefix(code)}{code}"


def eastmoney_secid(symbol: str) -> str:
    """
    Return the East Money secid, such as 1.600519.

    Args:
        symbol: Six-digit stock symbol.

    Returns:
        East Money secid string.
    """
    code = normalize_symbol(symbol)
    exchange = infer_exchange(code)
    if exchange == "SSE":
        return f"1.{code}"
    if exchange == "BSE":
        return f"2.{code}"
    if exchange == "SZSE":
        return f"0.{code}"
    raise StockException("Cannot infer East Money secid", symbol=symbol)
