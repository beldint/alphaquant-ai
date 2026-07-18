"""
Project: AlphaQuant AI
File: backend/tests/test_market_providers.py
Description: Unit tests for A-share market provider helpers and registrations.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.config import settings
from backend.core.config.settings import StockProviderName
from backend.core.exceptions import StockException
from backend.datasource.manager import stock_provider_manager
from backend.datasource.providers.sina_provider import _parse_sina_payload
from backend.datasource.providers.stock_code import (
    eastmoney_secid,
    exchange_prefix,
    infer_exchange,
    normalize_symbol,
    prefixed_symbol,
)
from backend.datasource.providers.tencent_provider import (
    _build_kline_bar,
    _parse_tencent_payload,
)


def test_a_share_symbol_helpers_normalize_exchange_codes() -> None:
    """A-share symbols should convert consistently for public data APIs."""
    assert normalize_symbol("sh600519") == "600519"
    assert normalize_symbol("SZ000001") == "000001"
    assert infer_exchange("600519") == "SSE"
    assert infer_exchange("000001") == "SZSE"
    assert exchange_prefix("830799") == "bj"
    assert prefixed_symbol("600519") == "sh600519"
    assert eastmoney_secid("000001") == "0.000001"
    assert eastmoney_secid("600519") == "1.600519"


def test_a_share_symbol_helpers_reject_invalid_symbols() -> None:
    """Invalid stock symbols should fail before outbound requests are made."""
    with pytest.raises(StockException):
        normalize_symbol("60051")


def test_tencent_quote_payload_parser_extracts_fields() -> None:
    """Tencent quote payload parser should preserve tilde-separated fields."""
    fields = [""] * 40
    fields[1] = "贵州茅台"
    fields[3] = "1688.88"
    payload = f'v_sh600519="{"~".join(fields)}";'

    parsed = _parse_tencent_payload(payload, "sh600519")

    assert parsed[1] == "贵州茅台"
    assert parsed[3] == "1688.88"


def test_sina_quote_payload_parser_extracts_fields() -> None:
    """Sina quote payload parser should preserve comma-separated fields."""
    fields = ["贵州茅台", "1680.00", "1670.00", "1688.88"] + ["0"] * 26
    fields.extend(["2026-07-17", "15:00:00"])
    payload = f'var hq_str_sh600519="{",".join(fields)}";'

    parsed = _parse_sina_payload(payload, "sh600519")

    assert parsed[0] == "贵州茅台"
    assert parsed[3] == "1688.88"


def test_tencent_kline_builder_filters_and_maps_rows() -> None:
    """Tencent Kline rows should map into the unified OHLCV schema."""
    row = ["2026-07-17", "10.00", "10.50", "10.80", "9.90", "123456"]

    bar = _build_kline_bar(
        "600519",
        row,
        date(2026, 7, 1),
        date(2026, 7, 31),
        StockProviderName.TENCENT,
    )

    assert bar is not None
    assert bar.symbol == "600519"
    assert bar.close_price == Decimal("10.50")
    assert bar.source == StockProviderName.TENCENT


def test_provider_priority_and_registration_include_configured_sources() -> None:
    """Configured provider priority should be backed by registered providers."""
    assert settings.stock_provider_priority[:3] == [
        StockProviderName.TENCENT,
        StockProviderName.SINA,
        StockProviderName.EASTMONEY,
    ]
    for provider_name in settings.stock_provider_priority:
        assert provider_name in stock_provider_manager.providers
    assert StockProviderName.TUSHARE not in stock_provider_manager.providers
    assert StockProviderName.BAOSTOCK not in stock_provider_manager.providers
