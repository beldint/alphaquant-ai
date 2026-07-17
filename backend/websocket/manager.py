"""
Project: AlphaQuant AI
File: backend/websocket/manager.py
Description: WebSocket connection manager for realtime dashboard updates.
Python Version: 3.11.9
"""

from __future__ import annotations

from collections import defaultdict

from fastapi import WebSocket
from loguru import logger


class WebSocketManager:
    """Manage WebSocket client connections by channel."""

    def __init__(self) -> None:
        """Initialize connection storage."""
        self._channels: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, channel: str) -> None:
        """
        Accept and register a WebSocket connection.

        Args:
            websocket: FastAPI WebSocket.
            channel: Subscription channel.
        """
        await websocket.accept()
        self._channels[channel].add(websocket)
        logger.info("WebSocket connected: channel={channel}", channel=channel)

    def disconnect(self, websocket: WebSocket, channel: str) -> None:
        """
        Remove a WebSocket connection.

        Args:
            websocket: FastAPI WebSocket.
            channel: Subscription channel.
        """
        self._channels[channel].discard(websocket)
        if not self._channels[channel]:
            self._channels.pop(channel, None)
        logger.info("WebSocket disconnected: channel={channel}", channel=channel)

    async def broadcast_json(self, channel: str, payload: dict[str, object]) -> None:
        """
        Broadcast JSON payload to all clients in a channel.

        Args:
            channel: Subscription channel.
            payload: JSON-compatible payload.
        """
        stale_connections: list[WebSocket] = []
        for websocket in self._channels.get(channel, set()).copy():
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                stale_connections.append(websocket)
        for websocket in stale_connections:
            self.disconnect(websocket, channel)


websocket_manager = WebSocketManager()

