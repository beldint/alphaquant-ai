
from __future__ import annotations
from fastapi import APIRouter
import httpx
from loguru import logger
from backend.core.responses import APIResponse, build_success_response

router = APIRouter(prefix="/market", tags=["market"])

EASTMONEY_URL = "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&fields=f2,f3,f4,f12,f14&secids=1.000001,0.399001,0.399006,1.000688"

NAME_MAP = {"1.000001":"上证指数","0.399001":"深证成指","0.399006":"创业板指","1.000688":"科创50"}

@router.get("/indices", response_model=APIResponse[list[dict]])
async def get_market_indices():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(EASTMONEY_URL)
            data = r.json()
            items = data.get("data", {}).get("diff", [])
            indices = []
            for item in items:
                sid = str(item.get("f12",""))
                indices.append({
                    "name": NAME_MAP.get(sid, sid),
                    "price": item.get("f2", 0),
                    "change": item.get("f4", 0),
                    "pct_change": item.get("f3", 0),
                })
            return build_success_response(indices)
    except Exception as exc:
        logger.warning("Failed to fetch market indices: {error}", error=str(exc))
        return build_success_response([])
