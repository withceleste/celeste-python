"""Closing a retained stream must release the consumer's request context."""

import asyncio
import gc
import weakref
from collections.abc import AsyncIterator
from contextvars import ContextVar

import pytest

from celeste.modalities.text.protocols.openresponses.client import (
    OpenResponsesTextStream,
)


class RequestState:
    pass


@pytest.mark.parametrize("eager", [False, True])
async def test_closed_stream_releases_caller_context(eager: bool) -> None:
    async def events() -> AsyncIterator[dict[str, str]]:
        yield {"type": "response.output_text.delta", "delta": "hello"}

    context: ContextVar[RequestState] = ContextVar("request-state")
    state = RequestState()
    reference = weakref.ref(state)
    token = context.set(state)
    loop = asyncio.get_running_loop()
    previous = loop.get_task_factory()
    loop.set_task_factory(asyncio.eager_task_factory if eager else None)
    try:
        stream = OpenResponsesTextStream(events())
        await anext(stream)
        await stream.aclose()
    finally:
        context.reset(token)
        loop.set_task_factory(previous)
    del state, token
    await asyncio.sleep(0)
    gc.collect()
    assert reference() is None
