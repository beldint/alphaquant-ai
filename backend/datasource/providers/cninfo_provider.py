"""
Project: AlphaQuant AI
File: backend/datasource/providers/cninfo_provider.py
Description: CNInfo official announcement and risk disclosure provider.
Python Version: 3.11.9
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field

from backend.core.config import settings
from backend.core.exceptions import StockException
from backend.datasource.providers.http_client import build_async_client
from backend.datasource.providers.stock_code import normalize_symbol

MARKET_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class CninfoAnnouncement(BaseModel):
    """Official announcement metadata from CNInfo."""

    symbol: str = Field(min_length=1)
    title: str = Field(min_length=1)
    published_at: datetime | None = None
    category: str | None = None
    url: str | None = None
    source: str = "cninfo"


class CninfoProvider:
    """Provider for official listed-company announcements from CNInfo."""

    def __init__(self) -> None:
        """Initialize reusable HTTP client."""
        self._http = build_async_client(
            timeout=settings.stock_request_timeout_seconds,
            headers={
                "User-Agent": MARKET_USER_AGENT,
                "Referer": "http://www.cninfo.com.cn/new/index",
            },
        )

    async def get_recent_announcements(
        self,
        symbol: str,
        *,
        page_size: int = 10,
    ) -> list[CninfoAnnouncement]:
        """
        Fetch recent official announcements for a stock.

        Args:
            symbol: Six-digit A-share symbol.
            page_size: Maximum number of records.

        Returns:
            Announcement metadata list.
        """
        code = normalize_symbol(symbol)
        url = f"{str(settings.cninfo_base_url).rstrip('/')}/new/hisAnnouncement/query"
        payload = {
            "pageNum": 1,
            "pageSize": max(1, min(page_size, 30)),
            "column": "szse",
            "tabName": "fulltext",
            "stock": code,
            "searchkey": "",
            "plate": "",
            "seDate": "",
            "isHLtitle": "true",
        }
        try:
            response = await self._http.post(str(url), data=payload)
            response.raise_for_status()
            data = response.json()
            rows = data.get("announcements") or []
            return [
                item
                for item in (_to_announcement(code, row) for row in rows)
                if item is not None
            ]
        except Exception as exc:
            logger.warning(
                "CNInfo announcement fetch failed: symbol={symbol} error={error}",
                symbol=code,
                error=str(exc),
            )
            raise StockException(
                "CNInfo announcement fetch failed",
                provider="cninfo",
                symbol=code,
                cause=exc,
            ) from exc

    async def get_risk_signals(self, symbol: str) -> dict[str, Any]:
        """
        Build risk signals from recent official announcements.

        Args:
            symbol: Six-digit A-share symbol.

        Returns:
            Compact risk signal dictionary.
        """
        announcements = await self.get_recent_announcements(symbol, page_size=20)
        risk_keywords = (
            "风险",
            "问询",
            "监管",
            "处罚",
            "诉讼",
            "仲裁",
            "退市",
            "减持",
            "质押",
            "冻结",
            "更正",
        )
        matched = [
            item
            for item in announcements
            if any(keyword in item.title for keyword in risk_keywords)
        ]
        return {
            "source": "cninfo",
            "announcement_count": len(announcements),
            "risk_count": len(matched),
            "latest_announcements": [
                item.model_dump(mode="json") for item in announcements[:5]
            ],
            "risk_announcements": [
                item.model_dump(mode="json") for item in matched[:5]
            ],
        }

    async def close(self) -> None:
        """Close HTTP resources."""
        await self._http.aclose()


def _to_announcement(symbol: str, row: dict[str, Any]) -> CninfoAnnouncement | None:
    title = (
        str(row.get("announcementTitle") or "")
        .replace("<em>", "")
        .replace("</em>", "")
        .strip()
    )
    if not title:
        return None
    adjunct_url = row.get("adjunctUrl")
    url = f"http://static.cninfo.com.cn/{adjunct_url}" if adjunct_url else None
    return CninfoAnnouncement(
        symbol=symbol,
        title=title,
        published_at=_parse_cninfo_time(row.get("announcementTime")),
        category=str(row.get("announcementTypeName") or "") or None,
        url=url,
    )


def _parse_cninfo_time(value: object) -> datetime | None:
    if value is None:
        return None
    try:
        timestamp = int(value)
        return datetime.fromtimestamp(timestamp / 1000).astimezone()
    except (TypeError, ValueError, OSError):
        return None
