"""WebSocket client for AI provider APIs using persistent connections."""

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from websockets.asyncio.client import ClientConnection
from websockets.asyncio.client import connect as ws_connect

from celeste.core import Modality, Provider

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60.0


class WebSocketClient:
    """Async WebSocket client wrapper.

    Provides a simple interface for WebSocket connections with:
    - Context manager pattern for automatic cleanup
    - JSON message helpers
    - Connection state management
    """

    async def connect(
        self,
        url: str,
        headers: dict[str, str] | None = None,
    ) -> "WebSocketConnection":
        """Open WebSocket connection.

        Args:
            url: WebSocket URL (wss:// or ws://).
            headers: Optional headers (e.g., authentication).

        Returns:
            WebSocketConnection for send/receive operations.
        """
        extra_headers = headers or {}
        ws = await ws_connect(url, additional_headers=extra_headers)
        return WebSocketConnection(ws)


class WebSocketConnection:
    """Active WebSocket connection wrapper."""

    def __init__(self, ws: ClientConnection) -> None:
        self._ws = ws

    async def send(self, message: str) -> None:
        """Send text message."""
        await self._ws.send(message)

    async def send_json(self, data: dict[str, Any]) -> None:
        """Send JSON message."""
        await self._ws.send(json.dumps(data))

    async def recv(self) -> str:
        """Receive text message."""
        message = await self._ws.recv()
        if isinstance(message, bytes):
            return message.decode("utf-8")
        return message

    async def recv_json(self) -> dict[str, Any]:
        """Receive and parse JSON message."""
        message = await self.recv()
        return json.loads(message)  # type: ignore[no-any-return]

    def __aiter__(self) -> AsyncIterator[str]:
        """Iterate over incoming messages."""
        return self._message_iterator()

    async def _message_iterator(self) -> AsyncIterator[str]:
        """Async iterator for incoming messages."""
        async for message in self._ws:
            if isinstance(message, bytes):
                yield message.decode("utf-8")
            else:
                yield message

    async def close(self) -> None:
        """Close connection."""
        await self._ws.close()

    async def __aenter__(self) -> "WebSocketConnection":
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Exit async context manager and close connection."""
        await self.close()


# Module-level registry (mirrors http.py pattern)
_ws_clients: dict[tuple[Provider, Modality], WebSocketClient] = {}


def get_ws_client(provider: Provider, modality: Modality) -> WebSocketClient:
    """Get or create shared WebSocket client for provider/modality.

    Args:
        provider: The AI provider.
        modality: The modality being used.

    Returns:
        Shared WebSocketClient instance for this provider and modality.
    """
    key = (provider, modality)
    if key not in _ws_clients:
        _ws_clients[key] = WebSocketClient()
    return _ws_clients[key]


async def close_all_ws_clients() -> None:
    """Close all WebSocket clients and clear registry."""
    _ws_clients.clear()


def clear_ws_clients() -> None:
    """Clear WebSocket client registry."""
    _ws_clients.clear()


__all__ = [
    "DEFAULT_TIMEOUT",
    "WebSocketClient",
    "WebSocketConnection",
    "clear_ws_clients",
    "close_all_ws_clients",
    "get_ws_client",
]
