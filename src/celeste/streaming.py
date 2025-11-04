"""Streaming support for Celeste."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from types import TracebackType
from typing import Any, Self

from celeste.io import Chunk, Output


class Stream[Out: Output](ABC):
    """Async iterator wrapper providing final Output access after stream exhaustion."""

    def __init__(
        self,
        sse_iterator: AsyncIterator[dict[str, Any]],
    ) -> None:
        """Initialize stream with SSE iterator."""
        self._sse_iterator = sse_iterator
        self._chunks: list[Chunk] = []
        self._closed = False
        self._output: Out | None = None

    @abstractmethod
    def _parse_chunk(self, event: dict[str, Any]) -> Chunk | None:
        """Parse SSE event into Chunk (returns None to filter lifecycle events)."""
        ...

    @abstractmethod
    def _parse_output(self, chunks: list[Chunk]) -> Out:
        """Parse final Output from accumulated chunks."""
        ...

    def __repr__(self) -> str:
        """Developer-friendly representation showing stream state."""
        if self._output:
            state = "done"
        elif self._closed:
            state = "closed"
        elif self._chunks:
            state = "streaming"
        else:
            state = "idle"

        chunks = f", {len(self._chunks)} chunks" if self._chunks else ""
        return f"<{self.__class__.__name__}: {state}{chunks}>"

    # AsyncIterator protocol
    def __aiter__(self) -> Self:
        """Return self as async iterator."""
        return self

    async def __anext__(self) -> Chunk:
        """Yield next chunk from stream."""
        if self._closed:
            raise StopAsyncIteration

        try:
            async for event in self._sse_iterator:
                chunk = self._parse_chunk(event)
                if chunk is not None:
                    self._chunks.append(chunk)
                    return chunk

            # Stream exhausted - validate and parse final output
            if not self._chunks:
                msg = "Stream completed but no chunks were produced"
                raise RuntimeError(msg)

            self._output = self._parse_output(self._chunks)
        except Exception:
            await self.aclose()
            raise

        # Only reached on successful exhaustion
        await self.aclose()
        raise StopAsyncIteration

    # AsyncContextManager protocol
    async def __aenter__(self) -> Self:
        """Enter context - return self for iteration."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """Exit context - ensure cleanup even on exception."""
        await self.aclose()
        return False  # Propagate exceptions

    @property
    def output(self) -> Out:
        """Access final Output after stream exhaustion (raises RuntimeError if not ready)."""
        if self._output is None:
            msg = "Stream not exhausted. Consume all chunks before accessing .output"
            raise RuntimeError(msg)
        return self._output

    async def aclose(self) -> None:
        """Explicitly close stream and cleanup resources."""
        if self._closed:
            return

        self._closed = True

        # Close SSE iterator (httpx-sse connection)
        if hasattr(self._sse_iterator, "aclose"):
            await self._sse_iterator.aclose()


__all__ = ["Stream"]
