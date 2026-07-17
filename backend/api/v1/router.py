"""
Project: AlphaQuant AI
File: backend/api/v1/router.py
Description: Version 1 API router aggregation.
Python Version: 3.11.9
"""
from __future__ import annotations
from fastapi import APIRouter
from backend.api.v1 import analysis, auth, health, stocks, ws

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(stocks.router)
api_router.include_router(analysis.router)
api_router.include_router(ws.router)
