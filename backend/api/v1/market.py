
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from random import uniform
from fastapi import APIRouter
from backend.core.responses import APIResponse, build_success_response

router = APIRouter(prefix="/market", tags=["market"])

async def _mock_index(name, base):
    change = round(uniform(-2, 2), 2)
    price = round(base + change, 2)
    pct = round(change / base * 100, 2)
    return {"name": name, "price": price, "change": change, "pct_change": pct, "timestamp": datetime.now().isoformat()}

@router.get("/indices", response_model=APIResponse[list[dict]])
async def get_market_indices():
    indices = [
        await _mock_index("上证指数", 3200),
        await _mock_index("深证成指", 10500),
        await _mock_index("创业板指", 2200),
        await _mock_index("科创50", 980),
    ]
    return build_success_response(indices)
