"""
Project: AlphaQuant AI
File: backend/api/v1/health.py
"""
from __future__ import annotations
from fastapi import APIRouter
from backend.cache.redis_client import check_redis_health
from backend.core.responses import APIResponse, build_success_response
from backend.database.session import check_database_health

router = APIRouter(prefix="/health", tags=["health"])

@router.get("", response_model=APIResponse[dict[str, bool]])
async def health_check() -> APIResponse[dict[str, bool]]:
    database_healthy = False
    redis_healthy = False
    try:
        database_healthy = await check_database_health()
    except:
        database_healthy = False
    try:
        redis_healthy = await check_redis_health()
    except:
        redis_healthy = False
    return build_success_response({
        "api": True, "database": database_healthy, "redis": redis_healthy,
    })
