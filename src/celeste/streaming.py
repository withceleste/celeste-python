"""Streaming support for Celeste."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from contextlib import AbstractContextManager, suppress
from types import TracebackType
from typing import Any, Self, Unpack

from anyio.from_thread import BlockingPortal, start_blocking_portal

from celeste.exceptions import StreamNotExhaustedError
from celeste.io import Chunk as ChunkBase
from celeste.io import Output
from celeste.parameters import Parameters


class Stream[Out: Output, Params: Parameters, Chunk: ChunkBase](ABC):
    """Async iterator wrapper providing final Output access after stream exhaustion.

    Supports both async iteration (`async for chunk in stream`) and sync iteration
    (`for chunk in stream`). Sync iteration uses anyio's blocking portal to maintain
    a persistent event loop in a dedicated thread.

    Note: For high-volume scenarios, async iteration is recommended. Sync iteration
    creates a background thread per stream.
    """

    def __init__(
        self,
        sse_iterator: AsyncIterator[dict[str, Any]],
        **parameters: Unpack[Params],  # type: ignore[misc]
    ) -> None:
        """Initialize stream with SSE iterator."""
        self._sse_iterator = sse_iterator
        self._chunks: list[Chunk] = []
        self._closed = False
        self._output: Out | None = None
        self._parameters = parameters
        # Sync iteration state
        self._portal: BlockingPortal | None = None
        self._portal_cm: AbstractContextManager[BlockingPortal] | None = None

    @abstractmethod
    def _parse_chunk(self, event: dict[str, Any]) -> Chunk | None:
        """Parse SSE event into Chunk (returns None to filter lifecycle events)."""
        ...

    @abstractmethod
    def _parse_output(self, chunks: list[Chunk], **parameters: Unpack[Params]) -> Out:  # type: ignore[misc]
        """Parse final Output from accumulated chunks."""
        ...

    def _build_stream_metadata(
        self, raw_events: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Build metadata for streaming. Providers override to filter content."""
        return {"raw_events": raw_events}

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

            # Stream exhausted naturally
            if self._chunks:
                self._output = self._parse_output(self._chunks, **self._parameters)
            self._closed = True
        except Exception:
            await self.aclose()
            raise

        raise StopAsyncIteration

    # Iterator protocol (sync)
    def __iter__(self) -> Self:
        """Return self as sync iterator with dedicated event loop.

        Creates a blocking portal that maintains a persistent event loop
        in a dedicated thread for consistent async context.
        """
        if self._portal is None:
            self._portal_cm = start_blocking_portal()
            self._portal = self._portal_cm.__enter__()
        return self

    def __next__(self) -> Chunk:
        """Yield next chunk via portal's persistent event loop."""
        if self._portal is None:
            self.__iter__()

        try:
            return self._portal.call(self.__anext__)  # type: ignore[union-attr,no-any-return]
        except StopAsyncIteration:
            self._cleanup_portal()
            raise StopIteration from None

    def _cleanup_portal(self) -> None:
        """Clean up the blocking portal and its thread."""
        if self._portal_cm is not None:
            # Close stream via portal before exiting (ensures _closed = True)
            if self._portal is not None and not self._closed:
                with suppress(RuntimeError):
                    self._portal.call(self.aclose)
            self._portal_cm.__exit__(None, None, None)
            self._portal = None
            self._portal_cm = None

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

    # ContextManager protocol (sync)
    def __enter__(self) -> Self:
        """Enter sync context - return self for iteration."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit sync context - ensure cleanup."""
        self._cleanup_portal()

    @property
    def output(self) -> Out:
        """Access final Output after stream exhaustion (raises StreamNotExhaustedError if not ready)."""
        if self._output is None:
            raise StreamNotExhaustedError()
        return self._output

    async def aclose(self) -> None:
        """Explicitly close stream and cleanup resources."""
        if self._closed:
            return

        self._closed = True

        # Fast path: skip if iterator is currently running
        if getattr(self._sse_iterator, "ag_running", False):
            return

        # Close SSE iterator (httpx-sse connection)
        # Use suppress to handle TOCTOU race between ag_running check and aclose
        if hasattr(self._sse_iterator, "aclose"):
            with suppress(RuntimeError):
                await self._sse_iterator.aclose()


__all__ = ["Stream"]
