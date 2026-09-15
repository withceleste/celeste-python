"""Small HTTPX helpers shared by transport regression tests."""

import json
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock, patch

import httpx

from celeste import Modality, Protocol, create_client
from celeste.auth import NoAuth
from celeste.http import HTTPClient
from celeste.modalities.text.client import TextClient


def _text_client() -> TextClient:
    return create_client(
        modality=Modality.TEXT,
        protocol=Protocol.OPENRESPONSES,
        model="test",
        base_url="https://example.test",
        auth=NoAuth(),
    )


def _sse(*events: dict[str, Any]) -> httpx.Response:
    return httpx.Response(
        200,
        headers={"content-type": "text/event-stream"},
        content="".join(f"data: {json.dumps(event)}\n\n" for event in events),
    )


@asynccontextmanager
async def _mock_http(
    handler: Callable[[httpx.Request], httpx.Response],
) -> AsyncIterator[None]:
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        with patch.object(HTTPClient, "_get_client", AsyncMock(return_value=http)):
            yield
