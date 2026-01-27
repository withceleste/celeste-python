"""Text streaming primitives."""

from abc import abstractmethod
from collections.abc import AsyncIterator, Callable
from typing import Any, Unpack

from celeste.client import ModalityClient
from celeste.pricing import Cost
from celeste.streaming import Stream
from celeste.types import TextContent

from .io import TextChunk, TextFinishReason, TextOutput, TextUsage
from .parameters import TextParameters


class TextStream(Stream[TextOutput, TextParameters, TextChunk]):
    """Streaming for text modality."""

    def __init__(
        self,
        sse_iterator: AsyncIterator[dict[str, Any]],
        transform_output: Callable[..., TextContent],
        client: ModalityClient,
        **parameters: Unpack[TextParameters],
    ) -> None:
        """Initialize stream with output transformation support."""
        super().__init__(sse_iterator, **parameters)
        self._transform_output = transform_output
        self._client = client

    @abstractmethod
    def _aggregate_content(self, chunks: list[TextChunk]) -> str:
        """Aggregate content from chunks into raw text."""
        ...

    def _aggregate_usage(self, chunks: list[TextChunk]) -> TextUsage:
        """Aggregate usage across chunks (universal)."""
        for chunk in reversed(chunks):
            if chunk.usage:
                return chunk.usage
        return TextUsage()

    def _aggregate_cost(self, chunks: list[TextChunk]) -> Cost | None:
        """Aggregate cost across chunks (use last chunk's cost or calculate from usage)."""
        # First try to find cost in chunks
        for chunk in reversed(chunks):
            if chunk.cost:
                return chunk.cost
        # Fall back to calculating from aggregated usage
        usage = self._aggregate_usage(chunks)
        return self._client._calculate_cost(usage)

    def _aggregate_finish_reason(
        self,
        chunks: list[TextChunk],
    ) -> TextFinishReason | None:
        """Aggregate finish reason across chunks (universal)."""
        for chunk in reversed(chunks):
            if chunk.finish_reason:
                return chunk.finish_reason
        return None

    @abstractmethod
    def _aggregate_event_data(self, chunks: list[TextChunk]) -> list[dict[str, Any]]:
        """Collect raw events (filtering happens in _build_stream_metadata)."""
        ...

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Build streaming metadata. Provider API Stream overrides to filter content."""
        return {
            "model": self._client.model.id,
            "provider": self._client.provider,
            "modality": self._client.modality,
            "raw_events": raw_events,
        }

    def _parse_output(
        self,
        chunks: list[TextChunk],
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Assemble chunks into final output."""
        raw_content = self._aggregate_content(chunks)
        content: TextContent = self._transform_output(raw_content, **parameters)
        raw_events = self._aggregate_event_data(chunks)
        usage = self._aggregate_usage(chunks)
        cost = self._aggregate_cost(chunks)

        # Track cost if tracker is configured
        if self._client.cost_tracker is not None:
            self._client.cost_tracker.add(cost)

        return TextOutput(
            content=content,
            usage=usage,
            finish_reason=self._aggregate_finish_reason(chunks),
            cost=cost,
            metadata=self._build_stream_metadata(raw_events),
        )


__all__ = ["TextStream"]
