"""HTTP client with persistent connection pooling for AI provider APIs."""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any

import httpx
from httpx_sse import aconnect_sse

from celeste.core import Modality, Protocol, Provider

logger = logging.getLogger(__name__)

MAX_CONNECTIONS = 20
MAX_KEEPALIVE_CONNECTIONS = 10
DEFAULT_TIMEOUT = 180.0
MAX_RETRIES = 2
RETRY_BASE_DELAY = 0.5
RETRYABLE_STATUS = frozenset({408, 429, 500, 502, 503, 504})


async def _retry_request(
    send: Callable[[], Awaitable[httpx.Response]],
) -> httpx.Response:
    """Retry `send` on transient failures (network errors + retryable status) with backoff, then fail hard."""
    for attempt in range(MAX_RETRIES):
        try:
            response = await send()
        except (httpx.TimeoutException, httpx.NetworkError):
            pass  # transient — retry after backoff
        else:
            if response.status_code not in RETRYABLE_STATUS:
                return response
        await asyncio.sleep(RETRY_BASE_DELAY * 2**attempt)
    return await send()


class HTTPClient:
    """Pool connections per loop and close them during async-generator shutdown.

    asyncio.run/Runner perform this shutdown automatically. Manually managed loops
    must await aclose() or loop.shutdown_asyncgens() before loop.close().
    """

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
        self._clients: dict[
            asyncio.AbstractEventLoop,
            tuple[httpx.AsyncClient, AsyncGenerator[httpx.AsyncClient, None]],
        ] = {}
        self._max_connections = max_connections
        self._max_keepalive_connections = max_keepalive_connections

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create httpx.AsyncClient with connection pooling."""
        current_loop = asyncio.get_running_loop()

        if current_loop not in self._clients:
            lifetime = self._client_lifetime()
            self._clients[current_loop] = (await anext(lifetime), lifetime)

        return self._clients[current_loop][0]

    async def _client_lifetime(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Register cleanup on the owning loop before handing out its client."""
        loop = asyncio.get_running_loop()
        limits = httpx.Limits(
            max_connections=self._max_connections,
            max_keepalive_connections=self._max_keepalive_connections,
        )
        client = httpx.AsyncClient(limits=limits)  # nosec B113
        try:
            yield client
        finally:
            self._clients.pop(loop, None)
            await client.aclose()

    async def post(
        self,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any],
        timeout: float = DEFAULT_TIMEOUT,
    ) -> httpx.Response:
        """Make POST request with connection pooling.

        No query-parameter support — encode query strings into `url`.

        Args:
            url: Full URL to POST to.
            headers: HTTP headers including authentication.
            json_body: JSON request body.
            timeout: Request timeout in seconds.

        Returns:
            HTTP response from the server.

        Raises:
            httpx.HTTPError: On network or timeout errors.
            ValueError: If URL is empty or invalid.
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")

        client = await self._get_client()
        return await _retry_request(
            lambda: client.post(
                url,
                headers=headers,
                json=json_body,
                timeout=timeout,
            )
        )

    async def post_multipart(
        self,
        url: str,
        headers: dict[str, str],
        files: dict[str, tuple[str, bytes, str]],
        data: dict[str, str],
        timeout: float = DEFAULT_TIMEOUT,
    ) -> httpx.Response:
        """Make POST request with multipart/form-data.

        Args:
            url: Full URL to POST to.
            headers: HTTP headers including authentication.
            files: File fields as dict mapping field_name -> (filename, content_bytes, mime_type).
            data: Form data fields as dict mapping field_name -> string value.
            timeout: Request timeout in seconds.

        Returns:
            HTTP response from the server.

        Raises:
            httpx.HTTPError: On network or timeout errors.
            ValueError: If URL is empty or invalid.
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")

        client = await self._get_client()
        return await _retry_request(
            lambda: client.post(
                url,
                headers=headers,
                files=files,
                data=data,
                timeout=timeout,
            )
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
            ValueError: If URL is empty or invalid.
        """
        if not url or not url.strip():
            raise ValueError("URL cannot be empty")

        client = await self._get_client()
        return await _retry_request(
            lambda: client.get(
                url,
                headers=headers or {},
                timeout=timeout,
                follow_redirects=follow_redirects,
            )
        )

    async def stream_post(
        self,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any],
        timeout: float = DEFAULT_TIMEOUT,
    ) -> AsyncGenerator[dict[str, Any], None]:
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
            if not event_source.response.is_success:
                await event_source.response.aread()
                event_source.response.raise_for_status()
            async for sse in event_source.aiter_sse():
                try:
                    yield json.loads(sse.data)
                except json.JSONDecodeError:
                    continue  # Skip non-JSON control messages (provider-agnostic)

    async def stream_post_ndjson(
        self,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any],
        timeout: float = DEFAULT_TIMEOUT,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Stream POST request using NDJSON (newline-delimited JSON).

        Unlike SSE (stream_post), NDJSON returns one JSON object per line.
        Used by Ollama's native API.

        Args:
            url: API endpoint URL.
            headers: HTTP headers (including authentication).
            json_body: JSON request body.
            timeout: Timeout in seconds (default: DEFAULT_TIMEOUT).

        Yields:
            Parsed JSON objects from NDJSON stream.
        """
        client = await self._get_client()
        async with client.stream(
            "POST",
            url,
            json=json_body,
            headers=headers,
            timeout=timeout,
        ) as response:
            if not response.is_success:
                await response.aread()
                response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    yield json.loads(line)

    async def aclose(self) -> None:
        """Close connections owned by the current event loop."""
        entry = self._clients.pop(asyncio.get_running_loop(), None)
        if entry is not None:
            await entry[1].aclose()

    async def __aenter__(self) -> "HTTPClient":
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args: Any) -> None:  # noqa: ANN401
        """Exit async context manager and cleanup connections."""
        await self.aclose()


# Shared wrappers stay registered while other threads may be creating their pools.
_http_clients: dict[tuple[Provider | Protocol, Modality], HTTPClient] = {}


def get_http_client(provider: Provider | Protocol, modality: Modality) -> HTTPClient:
    """Get or create shared HTTP client for provider and modality combination.

    Args:
        provider: The AI provider.
        modality: The modality being used.

    Returns:
        Shared HTTPClient instance for this provider and modality.
    """
    key = (provider, modality)
    if key not in _http_clients:
        return _http_clients.setdefault(key, HTTPClient())
    return _http_clients[key]


async def close_all_http_clients() -> None:
    """Close this event loop's HTTP clients, leaving other loops' pools intact."""
    for key, client in list(_http_clients.items()):
        try:
            await client.aclose()
        except Exception as e:
            logger.warning(f"Failed to close HTTP client for {key}: {e}")


def clear_http_clients() -> None:
    """Clear HTTP client registry without closing connections."""
    _http_clients.clear()


__all__ = [
    "DEFAULT_TIMEOUT",
    "MAX_CONNECTIONS",
    "MAX_KEEPALIVE_CONNECTIONS",
    "MAX_RETRIES",
    "HTTPClient",
    "clear_http_clients",
    "close_all_http_clients",
    "get_http_client",
]
