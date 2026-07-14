"""Public stream lifecycle, cleanup, and error contracts."""

from collections.abc import AsyncIterator
from typing import Any, ClassVar
from unittest.mock import Mock

import httpx
import pytest

from celeste.exceptions import StreamEventError, StreamNotExhaustedError
from celeste.io import Chunk, Output
from celeste.parameters import Parameters
from celeste.streaming import Stream, enrich_stream_errors


class TextOutput(Output[str]):
    """Concrete text output used by the stream contract tests."""


class TextStream(Stream[TextOutput, Parameters, Chunk[str]]):
    """Minimal stream using the production parsing and aggregation pipeline."""

    _chunk_class: ClassVar[type[Chunk[str]]] = Chunk[str]
    _output_class: ClassVar[type[Output[str]]] = TextOutput
    _empty_content: ClassVar[str] = ""

    def _parse_chunk_content(self, event_data: dict[str, Any]) -> str | None:
        return event_data.get("delta")

    def _aggregate_content(self, chunks: list[Chunk[str]]) -> str:
        return "".join(chunk.content for chunk in chunks)


class ClosableEvents:
    """Small async iterator that exposes whether cleanup reached its source."""

    def __init__(self, events: list[dict[str, Any]]) -> None:
        self._events = iter(events)
        self.close_calls = 0

    def __aiter__(self) -> "ClosableEvents":
        return self

    async def __anext__(self) -> dict[str, Any]:
        try:
            return next(self._events)
        except StopIteration as error:
            raise StopAsyncIteration from error

    async def aclose(self) -> None:
        self.close_calls += 1


async def events(*items: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
    for item in items:
        yield item


async def test_async_iteration_filters_lifecycle_events_and_builds_output() -> None:
    stream = TextStream(
        events(
            {"delta": "Hello"},
            {"type": "ping"},
            {"delta": " world"},
            {"type": "done"},
        )
    )

    chunks = [chunk async for chunk in stream]

    assert [chunk.content for chunk in chunks] == ["Hello", " world"]
    assert stream.output.content == "Hello world"
    assert stream.output is stream.output


async def test_output_is_unavailable_until_stream_is_exhausted() -> None:
    stream = TextStream(events({"delta": "Hello"}))

    with pytest.raises(StreamNotExhaustedError):
        _ = stream.output

    assert (await stream.__anext__()).content == "Hello"
    with pytest.raises(StreamNotExhaustedError):
        _ = stream.output

    with pytest.raises(StopAsyncIteration):
        await stream.__anext__()
    assert stream.output.content == "Hello"


async def test_empty_stream_completes_without_an_output() -> None:
    stream = TextStream(events({"type": "ping"}, {"type": "done"}))

    assert [chunk async for chunk in stream] == []
    with pytest.raises(StreamNotExhaustedError):
        _ = stream.output


async def test_aclose_is_idempotent_and_closes_the_source() -> None:
    source = ClosableEvents([{"delta": "unused"}])
    stream = TextStream(source)

    await stream.aclose()
    await stream.aclose()

    assert source.close_calls == 1
    with pytest.raises(StopAsyncIteration):
        await stream.__anext__()


async def test_async_context_closes_after_early_exit() -> None:
    source = ClosableEvents([{"delta": "first"}, {"delta": "second"}])

    async with TextStream(source) as stream:
        assert (await stream.__anext__()).content == "first"

    assert source.close_calls == 1
    with pytest.raises(StreamNotExhaustedError):
        _ = stream.output


async def test_source_failure_closes_the_stream() -> None:
    async def failing_events() -> AsyncIterator[dict[str, Any]]:
        yield {"delta": "first"}
        raise ConnectionError("connection lost")

    stream = TextStream(failing_events())

    with pytest.raises(ConnectionError, match="connection lost"):
        _ = [chunk async for chunk in stream]
    with pytest.raises(StopAsyncIteration):
        await stream.__anext__()


def test_sync_iteration_builds_the_same_output() -> None:
    stream = TextStream(events({"delta": "Hello"}, {"delta": " sync"}))

    assert [chunk.content for chunk in stream] == ["Hello", " sync"]
    assert stream.output.content == "Hello sync"


@pytest.mark.parametrize(
    ("event", "error_type", "message"),
    [
        (
            {
                "type": "error",
                "error": {"type": "overloaded_error", "message": "overloaded"},
            },
            "overloaded_error",
            "overloaded",
        ),
        (
            {"error": {"type": "invalid_request", "message": "bad request"}},
            "invalid_request",
            "bad request",
        ),
        (
            {"error": {"code": "rate_limit", "message": "slow down"}},
            "rate_limit",
            "slow down",
        ),
        (
            {"type": "error", "error": "provider failed"},
            None,
            "provider failed",
        ),
        (
            {"error": {"type": "unknown"}},
            "unknown",
            "Unknown error",
        ),
    ],
    ids=["typed", "field", "code", "string", "missing-message"],
)
async def test_stream_error_shapes(
    event: dict[str, Any], error_type: str | None, message: str
) -> None:
    stream = TextStream(
        events(event),
        stream_metadata={"provider": "test-provider"},
    )

    with pytest.raises(StreamEventError, match=message) as caught:
        _ = [chunk async for chunk in stream]

    assert caught.value.error_type == error_type
    assert caught.value.provider == "test-provider"
    assert caught.value.event_data == event


async def test_provider_can_override_error_type_fields() -> None:
    class GoogleLikeStream(TextStream):
        _error_type_fields = ("status", "code")

    stream = GoogleLikeStream(
        events(
            {
                "error": {
                    "status": "PERMISSION_DENIED",
                    "code": 403,
                    "message": "forbidden",
                }
            }
        )
    )

    with pytest.raises(StreamEventError) as caught:
        _ = [chunk async for chunk in stream]
    assert caught.value.error_type == "PERMISSION_DENIED"


async def test_midstream_error_preserves_already_yielded_chunks() -> None:
    stream = TextStream(
        events(
            {"delta": "partial"},
            {"type": "error", "error": {"message": "failed"}},
        )
    )
    chunks: list[Chunk[str]] = []

    with pytest.raises(StreamEventError, match="failed"):
        async for chunk in stream:
            chunks.append(chunk)

    assert [chunk.content for chunk in chunks] == ["partial"]


async def test_enrich_stream_errors_delegates_http_response() -> None:
    response = httpx.Response(
        401,
        request=httpx.Request("POST", "https://example.test/v1/chat"),
    )

    async def failing_events() -> AsyncIterator[dict[str, Any]]:
        raise httpx.HTTPStatusError(
            "unauthorized",
            request=response.request,
            response=response,
        )
        yield {}

    handler = Mock(side_effect=RuntimeError("enriched provider error"))

    with pytest.raises(RuntimeError, match="enriched provider error"):
        _ = [event async for event in enrich_stream_errors(failing_events(), handler)]
    handler.assert_called_once_with(response)


async def test_enrich_stream_errors_passes_successful_events_through() -> None:
    source_events = [{"delta": "Hello"}, {"delta": " world"}]

    result = [
        event
        async for event in enrich_stream_errors(
            events(*source_events),
            Mock(),
        )
    ]

    assert result == source_events
