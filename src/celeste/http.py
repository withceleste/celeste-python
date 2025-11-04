"""HTTP client with persistent connection pooling for AI provider APIs."""

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx
from httpx_sse import aconnect_sse

from celeste.core import Capability, Provider

logger = logging.getLogger(__name__)

MAX_CONNECTIONS = 20
MAX_KEEPALIVE_CONNECTIONS = 10
DEFAULT_TIMEOUT = 60.0


class HTTPClient:
    """Async HTTP client with persistent connection pooling."""

    def __init__(
        self,
        max_connections: int = MAX_CONNECTIONS,
        max_keepalive_connections: int = MAX_KEEPALIVE_CONNECTIONS,
    ) -> None:
        """Initialize HTTP client with connection pool limits.

        Args:
            max_connections: Maximum total connections in pool.
            max_keepalive_connections: Maximum idle keepalive connections.
        """
        self._client: httpx.AsyncClient | None = None
        self._max_connections = max_connections
        self._max_keepalive_connections = max_keepalive_connections

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create httpx.AsyncClient with connection pooling."""
        if self._client is None:
            limits = httpx.Limits(
                max_connections=self._max_connections,
                max_keepalive_connections=self._max_keepalive_connections,
            )
            self._client = httpx.AsyncClient(limits=limits)  # nosec B113
        return self._client

    async def post(
        self,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any],
        timeout: float = DEFAULT_TIMEOUT,
    ) -> httpx.Response:
        """Make POST request with connection pooling.

        Args:
            url: Full URL to POST to.
            headers: HTTP headers including authentication.
            json_body: JSON request body.
            timeout: Request timeout in seconds.

        Returns:
            HTTP response from the server.

        Raises:
            httpx.HTTPError: On network or timeout errors.
        """
        client = await self._get_client()
        return await client.post(
            url,
            headers=headers,
            json=json_body,
            timeout=timeout,
        )

    async def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        follow_redirects: bool = True,
    ) -> httpx.Response:
        """Make GET request with connection pooling.

        Args:
            url: Full URL to GET.
            headers: HTTP headers including authentication (optional).
            timeout: Request timeout in seconds.
            follow_redirects: Whether to follow HTTP redirects (default: True).

        Returns:
            HTTP response from the server.

        Raises:
            httpx.HTTPError: On network or timeout errors.
        """
        client = await self._get_client()
        return await client.get(
            url,
            headers=headers or {},
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

    async def stream_post(
        self,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any],
        timeout: float = DEFAULT_TIMEOUT,
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream POST request using Server-Sent Events.

        Args:
            url: API endpoint URL.
            headers: HTTP headers (including authentication).
            json_body: JSON request body.
            timeout: Timeout in seconds (default: DEFAULT_TIMEOUT).

        Yields:
            Parsed JSON events from SSE stream.
        """
        client = await self._get_client()

        async with aconnect_sse(
            client,
            "POST",
            url,
            json=json_body,
            headers=headers,
            timeout=timeout,
        ) as event_source:
            async for sse in event_source.aiter_sse():
                try:
                    yield json.loads(sse.data)
                except json.JSONDecodeError:
                    continue  # Skip non-JSON control messages (provider-agnostic)

    async def aclose(self) -> None:
        """Close HTTP client and cleanup all connections."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "HTTPClient":
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: Any) -> None:  # noqa: ANN401
        """Exit async context manager and cleanup connections."""
        await self.aclose()


# Module-level registry of shared HTTPClient instances
_http_clients: dict[tuple[Provider, Capability], HTTPClient] = {}


def get_http_client(provider: Provider, capability: Capability) -> HTTPClient:
    """Get or create shared HTTP client for provider and capability combination.

    Args:
        provider: The AI provider.
        capability: The capability being used.

    Returns:
        Shared HTTPClient instance for this provider and capability.
    """
    key = (provider, capability)

    if key not in _http_clients:
        _http_clients[key] = HTTPClient()

    return _http_clients[key]


async def close_all_http_clients() -> None:
    """Close all HTTP clients gracefully and clear registry."""
    for key, client in list(_http_clients.items()):
        try:
            await client.aclose()
        except Exception as e:
            logger.warning(f"Failed to close HTTP client for {key}: {e}")

    _http_clients.clear()


def clear_http_clients() -> None:
    """Clear HTTP client registry without closing connections."""
    _http_clients.clear()


__all__ = [
    "DEFAULT_TIMEOUT",
    "MAX_CONNECTIONS",
    "MAX_KEEPALIVE_CONNECTIONS",
    "HTTPClient",
    "clear_http_clients",
    "close_all_http_clients",
    "get_http_client",
]
