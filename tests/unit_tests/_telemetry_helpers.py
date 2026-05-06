"""Shared fixtures and helpers for telemetry-related unit tests."""

from collections.abc import AsyncIterator
from typing import Any, ClassVar, Unpack

from celeste.io import Chunk, Output, Usage
from celeste.parameters import Parameters
from celeste.streaming import Stream


class TelemetryUsage(Usage):
    """Usage with the full GenAI semconv field set used across telemetry tests."""

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    reasoning_tokens: int | None = None
    cached_tokens: int | None = None


class TelemetryOutput(Output[str]):
    """String-content Output used across telemetry tests."""


class TelemetryStream(Stream[TelemetryOutput, Parameters, Chunk]):
    """Concrete Stream that aggregates content + usage from per-chunk events."""

    _usage_class: ClassVar[type[Usage]] = TelemetryUsage
    _chunk_class: ClassVar[type[Chunk]] = Chunk
    _output_class: ClassVar[type[Output]] = TelemetryOutput
    _empty_content: ClassVar[str] = ""

    def __init__(
        self,
        sse_iterator: AsyncIterator[dict[str, Any]],
        stream_metadata: dict[str, Any] | None = None,
        **parameters: Unpack[Parameters],
    ) -> None:
        """Default `stream_metadata={"model": "test-model"}` to mirror production wiring."""
        super().__init__(
            sse_iterator,
            stream_metadata=stream_metadata or {"model": "test-model"},
            **parameters,
        )

    def _aggregate_content(self, chunks: list[Chunk]) -> str:
        """Concatenate chunk content."""
        return "".join(chunk.content for chunk in chunks)

    def _parse_chunk(self, event: dict[str, Any]) -> Chunk | None:
        """Parse delta events; lifecycle events return None."""
        content = event.get("delta")
        if not content and "usage" not in event:
            return None
        usage = TelemetryUsage(**event["usage"]) if "usage" in event else None
        return Chunk(content=content or "", finish_reason=None, usage=usage)


async def async_iter(events: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    """Convert a list of events into an async iterator."""
    for event in events:
        yield event
