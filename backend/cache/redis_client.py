"""
Project: AlphaQuant AI
File: backend/cache/redis_client.py
Description: Async Redis cache client with JSON serialization and TTL support.
Python Version: 3.11.9
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


class RedisCache:
    """High-level async Redis cache wrapper."""

    def __init__(self, redis: Redis) -> None:
        """
        Initialize cache wrapper.

        Args:
            redis: Async Redis client instance.
        """
        self.redis = redis

    async def get_json(self, key: str) -> dict[str, Any] | list[Any] | None:
        """
        Get a JSON value from Redis.

        Args:
            key: Cache key.

        Returns:
            Decoded JSON object, list, or None.
        """
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            decoded = value.decode("utf-8") if isinstance(value, bytes) else str(value)
            loaded = json.loads(decoded)
            if isinstance(loaded, (dict, list)):
                return loaded
            raise CacheException("Cached JSON value must be an object or array", key=key)
        except (RedisError, json.JSONDecodeError) as exc:
            logger.exception("Failed to read cache key={key}", key=key)
            raise CacheException(key=key, cause=exc) from exc

    async def set_json(
        self,
        key: str,
        value: Mapping[str, Any] | list[Any],
        *,
        ttl_seconds: int | None = None,
    ) -> None:
        """
        Store a JSON-serializable value in Redis.

        Args:
            key: Cache key.
            value: JSON-compatible mapping or list.
            ttl_seconds: Optional TTL in seconds.
        """
        ttl = ttl_seconds or settings.cache_default_ttl_seconds
        try:
            payload = json.dumps(value, ensure_ascii=False, default=str)
            await self.redis.set(key, payload, ex=ttl)
        except (RedisError, TypeError, ValueError) as exc:
            logger.exception("Failed to write cache key={key}", key=key)
            raise CacheException(key=key, cause=exc) from exc

    async def delete(self, key: str) -> int:
        """
        Delete a cache key.

        Args:
            key: Cache key.

        Returns:
            Number of deleted keys.
        """
        try:
            return int(await self.redis.delete(key))
        except Exception as exc:
            logger.warning("Failed to delete cache key={key}", key=key)
            raise CacheException(key=key, cause=exc) from exc

    async def exists(self, key: str) -> bool:
        """
        Check whether a key exists.

        Args:
            key: Cache key.

        Returns:
            True if the key exists.
        """
        try:
            return bool(await self.redis.exists(key))
        except RedisError as exc:
            logger.exception("Failed to check cache key={key}", key=key)
            raise CacheException(key=key, cause=exc) from exc

    async def close(self) -> None:
        """Close Redis client connections."""
        await self.redis.aclose()


def create_redis_client() -> Redis:
    """
    Create the shared async Redis client.

    Returns:
        Configured async Redis client.
    """
    return Redis.from_url(
        settings.redis_cache_url,
        socket_timeout=settings.redis_socket_timeout_seconds,
        health_check_interval=settings.redis_health_check_interval_seconds,
        decode_responses=False,
    )


redis_client = create_redis_client()
redis_cache = RedisCache(redis_client)


async def check_redis_health() -> bool:
    """
    Check whether Redis is reachable.

    Returns:
        True when Redis responds to ping.
    """
    try:
        return bool(await redis_client.ping())
    except RedisError as exc:
        logger.error("Redis health check failed: {error}", error=str(exc))
        return False

