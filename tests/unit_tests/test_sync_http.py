"""Connection pool ownership across synchronous calls."""

import asyncio
from typing import Any
from unittest.mock import patch

import httpx
import pytest
from asgiref.sync import async_to_sync

from celeste.http import HTTPClient, close_all_http_clients

from ._http_helpers import _sse, _text_client


@pytest.mark.parametrize("mode", ["unary", "stream", "asyncio"])
def test_owned_loops_close_pools_on_success_and_failure(mode: str) -> None:
    created: list[httpx.AsyncClient] = []
    constructor = httpx.AsyncClient
    calls = 0

    def handle(_: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 3:
            return httpx.Response(400, json={"error": {"message": "bad request"}})
        if mode == "stream":
            return _sse({"type": "response.output_text.delta", "delta": "ok"})
        return httpx.Response(
            200,
            json={
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": "ok"}],
                    }
                ],
            },
        )

    def make_client(**kwargs: Any) -> httpx.AsyncClient:  # noqa: ANN401
        http = constructor(transport=httpx.MockTransport(handle), **kwargs)
        created.append(http)
        return http

    client = _text_client()

    def generate() -> str:
        if mode == "unary":
            return client.sync.generate("hello").content
        if mode == "asyncio":
            return asyncio.run(client.generate("hello")).content
        stream = client.stream.generate("hello")
        _ = list(stream)
        return stream.output.content

    with patch("celeste.http.httpx.AsyncClient", make_client):
        assert generate() == generate() == "ok"
        with pytest.raises(httpx.HTTPStatusError, match="bad request"):
            generate()
    assert len(created) == 3
    assert all(http.is_closed for http in created)
    assert not client.http_client._clients


@pytest.mark.parametrize("mode", ["sync", "asyncio"])
async def test_owned_loop_cleanup_preserves_another_event_loops_pool(mode: str) -> None:
    pool = _text_client().http_client
    original = await pool._get_client()
    try:
        other = await asyncio.to_thread(
            lambda: (
                async_to_sync(pool._get_client)()
                if mode == "sync"
                else asyncio.run(pool._get_client())
            )
        )
        assert other.is_closed
        assert await pool._get_client() is original
        assert not original.is_closed
        assert len(pool._clients) == 1
    finally:
        await close_all_http_clients()


def test_runner_keeps_pool_between_calls_and_closes_after_cancellation() -> None:
    pool = HTTPClient()

    async def cancel() -> None:
        await pool._get_client()
        raise asyncio.CancelledError

    with asyncio.Runner() as runner:
        http = runner.run(pool._get_client())
        assert runner.run(pool._get_client()) is http
        with pytest.raises(asyncio.CancelledError):
            runner.run(cancel())
        assert not http.is_closed
    assert http.is_closed
    assert not pool._clients
