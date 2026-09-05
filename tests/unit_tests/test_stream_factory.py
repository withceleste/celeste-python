"""Lazy transport factories and shared stream ownership."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from celeste.protocols.openresponses.client import OpenResponsesClient
from celeste.streaming import enrich_stream_errors

from ._http_helpers import _text_client


@pytest.mark.parametrize("started", [False, True])
async def test_stream_factory_runs_only_on_first_pull(started: bool) -> None:
    closed = []

    async def events() -> AsyncGenerator[dict[str, Any], None]:
        try:
            yield {"type": "response.output_text.delta", "delta": "hello"}
        finally:
            closed.append(True)

    factory = AsyncMock(return_value=events())
    with patch.object(OpenResponsesClient, "_make_stream_request", factory):
        stream = _text_client().stream.generate("hello")
        factory.assert_not_called()
        if started:
            assert (await anext(stream)).content == "hello"
        await stream.aclose()
        assert factory.await_count == int(started)
        assert closed == ([True] if started else [])


async def test_close_cancels_a_pending_stream_factory() -> None:
    started, cancelled = asyncio.Event(), asyncio.Event()

    async def factory(
        *args: object, **kwargs: object
    ) -> AsyncGenerator[dict[str, Any], None]:
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()
        raise AssertionError("factory should be cancelled")

    with patch.object(OpenResponsesClient, "_make_stream_request", factory):
        stream = _text_client().stream.generate("hello")
        pending = asyncio.create_task(anext(stream))
        await asyncio.wait_for(started.wait(), 2)
        await asyncio.wait_for(stream.aclose(), 2)
        assert cancelled.is_set()
        with pytest.raises(asyncio.CancelledError):
            await pending


@pytest.mark.parametrize("failure", ["factory", "iteration", None])
async def test_stream_factory_enriches_errors_and_closes(failure: str | None) -> None:
    response = httpx.Response(
        401, request=httpx.Request("POST", "https://example.test/v1/chat")
    )
    closed = []

    async def events() -> AsyncGenerator[dict[str, Any], None]:
        try:
            if failure == "iteration":
                response.raise_for_status()
            yield {"delta": "hello"}
        finally:
            closed.append(True)

    async def factory() -> AsyncGenerator[dict[str, Any], None]:
        if failure == "factory":
            response.raise_for_status()
        return events()

    handler = Mock(side_effect=RuntimeError("enriched provider error"))
    stream = enrich_stream_errors(factory, handler)
    if failure:
        with pytest.raises(RuntimeError, match="enriched provider error"):
            _ = [event async for event in stream]
        handler.assert_called_once_with(response)
    else:
        assert [event async for event in stream] == [{"delta": "hello"}]
        handler.assert_not_called()
    assert closed == ([] if failure == "factory" else [True])
