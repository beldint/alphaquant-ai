"""
Project: AlphaQuant AI
File: backend/api/v1/ws.py
Description: WebSocket API routes for realtime subscriptions.
Python Version: 3.11.9
"""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from backend.websocket.manager import websocket_manager


router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str) -> None:
    """
    Subscribe to a realtime WebSocket channel.

    Args:
        websocket: WebSocket connection.
        channel: Subscription channel name.
    """
    await websocket_manager.connect(websocket, channel)
    try:
        while True:
            message = await websocket.receive_json()
            await websocket.send_json(
                {
                    "type": "ack",
                    "channel": channel,
                    "message": message,
                },
            )
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, channel)
    except RuntimeError as exc:
        logger.warning(
            "WebSocket runtime error: channel={channel} error={error}",
            channel=channel,
            error=str(exc),
        )
        websocket_manager.disconnect(websocket, channel)

