"""
Project: AlphaQuant AI
File: backend/cache/redis_client.py
Description: Async Redis cache client. Fully lazy - never connects at import time.
"""
from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any
from loguru import logger
from redis.asyncio import Redis
from redis.exceptions import RedisError
from backend.core.config import settings
from backend.core.exceptions import CacheException

_redis_client_instance: Redis | None = None
_redis_cache_instance: RedisCache | None = None

def _get_client() -> Redis:
    global _redis_client_instance
    if _redis_client_instance is None:
        try:
            _redis_client_instance = Redis.from_url(
                str(settings.redis_url),
                socket_timeout=settings.redis_socket_timeout_seconds,
                health_check_interval=settings.redis_health_check_interval_seconds,
                decode_responses=False,
            )
        except Exception as exc:
            logger.warning("Redis client creation failed: {error}", error=str(exc))
            return None
    return _redis_client_instance

class RedisCache:
    def __init__(self):
        self._redis = None
    
    async def _get_redis(self):
        if self._redis is None:
            self._redis = _get_client()
        return self._redis

    async def get_json(self, key: str) -> dict[str, Any] | list[Any] | None:
        client = await self._get_redis()
        if client is None:
            return None
        try:
            value = await client.get(key)
            if value is None:
                return None
            decoded = value.decode("utf-8") if isinstance(value, bytes) else str(value)
            loaded = json.loads(decoded)
            if isinstance(loaded, (dict, list)):
                return loaded
            raise CacheException("Cached JSON value must be an object or array", key=key)
        except Exception as exc:
            logger.warning("Failed to read cache key={key}: {error}", key=key, error=str(exc))
            return None

    async def set_json(self, key: str, value: Mapping[str, Any] | list[Any], *, ttl_seconds: int | None = None) -> None:
        client = await self._get_redis()
        if client is None:
            return
        ttl = ttl_seconds or settings.cache_default_ttl_seconds
        try:
            payload = json.dumps(value, ensure_ascii=False, default=str)
            await client.set(key, payload, ex=ttl)
        except Exception as exc:
            logger.warning("Failed to write cache key={key}: {error}", key=key, error=str(exc))

    async def delete(self, key: str) -> int:
        client = await self._get_redis()
        if client is None:
            return 0
        try:
            return int(await client.delete(key))
        except Exception as exc:
            logger.warning("Failed to delete cache key={key}: {error}", key=key, error=str(exc))
            return 0

    async def exists(self, key: str) -> bool:
        client = await self._get_redis()
        if client is None:
            return False
        try:
            return bool(await client.exists(key))
        except Exception as exc:
            logger.warning("Failed to check cache key={key}: {error}", key=key, error=str(exc))
            return False

    async def close(self) -> None:
        client = await self._get_redis()
        if client is None:
            return
        try:
            await client.aclose()
        except Exception as exc:
            logger.warning("Failed to close Redis: {error}", error=str(exc))
        finally:
            self._redis = None

redis_cache = RedisCache()

async def check_redis_health() -> bool:
    return False
