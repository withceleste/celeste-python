"""High-value tests for Stream - focusing on lifecycle, resource cleanup, and state management."""

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock

import pytest
from pydantic import Field

from celeste.io import Chunk, FinishReason, Output, Usage
from celeste.streaming import Stream


class ConcreteOutput(Output[str]):
    """Concrete output for testing Stream."""

    pass


class ConcreteStream(Stream[ConcreteOutput]):
    """Concrete Stream implementation for testing abstract behavior."""

    def __init__(
        self,
        sse_iterator: AsyncIterator[dict[str, Any]],
        chunk_events: list[dict[str, Any]] | None = None,
        filter_none: bool = False,
    ) -> None:
        """Initialize stream with configurable parsing behavior.

        Args:
            sse_iterator: Server-Sent Events iterator.
            chunk_events: Events that should be converted to chunks.
            filter_none: If True, return None for events not in chunk_events.
        """
        super().__init__(sse_iterator)
        self._chunk_events = chunk_events or []
        self._filter_none = filter_none

    def _parse_chunk(self, event: dict[str, Any]) -> Chunk | None:
        """Parse event to Chunk or None (for lifecycle events)."""
        # If filter_none enabled, only return chunks for events in chunk_events
        if self._filter_none and event not in self._chunk_events:
            return None

        content = event.get("delta", event.get("content", ""))
        if not content:
            return None

        return Chunk(
            content=content,
            finish_reason=None,  # Base tests don't use typed finish reasons
            metadata=event.get("metadata", {}),
        )

    def _parse_output(self, chunks: list[Chunk]) -> ConcreteOutput:
        """Combine chunks into final output."""
        content = "".join(chunk.content for chunk in chunks)
        # Usage is empty base class - store data in metadata for tests
        usage = Usage()
        return ConcreteOutput(
            content=content,
            usage=usage,
            metadata=chunks[-1].metadata if chunks else {},
        )


@pytest.fixture
def mock_sse_iterator() -> AsyncMock:
    """Create mock SSE iterator with aclose capability."""
    mock_iter = AsyncMock(spec=["aclose", "__anext__"])
    mock_iter.aclose = AsyncMock()
    return mock_iter


async def _async_iter(items: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    """Convert list to async iterator."""
    for item in items:
        yield item


class TestStreamAsyncIterator:
    """Test Stream AsyncIterator protocol - chunk filtering and exhaustion."""

    async def test_iteration_yields_chunks_and_filters_none(self) -> None:
        """Stream must filter None chunks (lifecycle events) and only yield valid chunks."""
        # Arrange - Mix of valid chunks and lifecycle events
        events = [
            {"delta": "Hello"},  # Valid chunk
            {"type": "ping"},  # Lifecycle event (no delta)
            {"delta": " world"},  # Valid chunk
            {"finish_reason": "stop"},  # Lifecycle event (no delta)
        ]
        stream = ConcreteStream(_async_iter(events))

        # Act - Collect chunks via iteration
        chunks = [chunk async for chunk in stream]

        # Assert - Only valid chunks yielded, lifecycle events filtered
        assert len(chunks) == 2
        assert chunks[0].content == "Hello"
        assert chunks[1].content == " world"

    async def test_iteration_stops_when_sse_exhausted(self) -> None:
        """Stream must raise StopAsyncIteration when SSE iterator is exhausted."""
        # Arrange
        events = [{"delta": "test"}]
        stream = ConcreteStream(_async_iter(events))

        # Act - Consume all chunks
        chunks = [chunk async for chunk in stream]

        # Assert - One chunk yielded
        assert len(chunks) == 1

        # Act & Assert - Next iteration raises StopAsyncIteration
        with pytest.raises(StopAsyncIteration):
            await stream.__anext__()

    async def test_iteration_when_closed_raises_stop_iteration(self) -> None:
        """Stream must raise StopAsyncIteration immediately if already closed."""
        # Arrange
        events = [{"delta": "test"}]
        stream = ConcreteStream(_async_iter(events))
        await stream.aclose()

        # Act & Assert - Closed stream raises StopAsyncIteration
        with pytest.raises(StopAsyncIteration):
            await stream.__anext__()

    async def test_stream_accumulates_chunks_internally(self) -> None:
        """Stream must accumulate all non-None chunks for later output parsing."""
        # Arrange
        events = [
            {"delta": "First"},
            {"type": "lifecycle"},  # Filtered
            {"delta": "Second"},
            {"delta": "Third"},
        ]
        stream = ConcreteStream(_async_iter(events))

        # Act - Consume stream
        async for _ in stream:
            pass

        # Assert - Verify internal accumulation via output
        assert stream.output.content == "FirstSecondThird"


class TestStreamOutputProperty:
    """Test Stream.output property - access guard and final result."""

    async def test_output_access_before_exhaustion_raises_error(self) -> None:
        """Accessing .output before stream exhaustion must raise RuntimeError."""
        # Arrange
        events = [{"delta": "test"}]
        stream = ConcreteStream(_async_iter(events))

        # Act & Assert - Premature access raises RuntimeError
        with pytest.raises(
            RuntimeError, match=r"Stream not exhausted\. Consume all chunks"
        ):
            _ = stream.output

    async def test_output_accessible_after_exhaustion(self) -> None:
        """Stream.output must be accessible after stream is fully consumed."""
        # Arrange
        events = [
            {"delta": "Hello", "metadata": {"usage": {"input_tokens": 5}}},
            {
                "delta": " world",
                "finish_reason": "stop",
                "metadata": {"usage": {"output_tokens": 10}},
            },
        ]
        stream = ConcreteStream(_async_iter(events))

        # Act - Consume stream
        async for _ in stream:
            pass

        # Assert - Output accessible with accumulated content
        output = stream.output
        assert output.content == "Hello world"
        # Usage is empty base class - data stored in metadata
        assert output.metadata.get("usage", {}).get("output_tokens") == 10

    async def test_output_returns_consistent_result_after_exhaustion(self) -> None:
        """Stream.output must return the same result on multiple accesses."""
        # Arrange
        events = [{"delta": "test"}]
        stream = ConcreteStream(_async_iter(events))

        # Act - Exhaust stream
        async for _ in stream:
            pass

        # Assert - Multiple accesses return identical result
        output1 = stream.output
        output2 = stream.output
        assert output1 is output2
        assert output1.content == "test"


class TestStreamResourceCleanup:
    """Test Stream resource cleanup - aclose() idempotence and SSE cleanup."""

    async def test_aclose_is_idempotent(self, mock_sse_iterator: AsyncMock) -> None:
        """Stream.aclose() must be safe to call multiple times without error."""
        # Arrange
        stream = ConcreteStream(mock_sse_iterator)

        # Act - Call aclose multiple times
        await stream.aclose()
        await stream.aclose()
        await stream.aclose()

        # Assert - No errors raised, SSE iterator closed once
        assert stream._closed is True
        mock_sse_iterator.aclose.assert_called_once()

    async def test_aclose_calls_sse_iterator_aclose(
        self, mock_sse_iterator: AsyncMock
    ) -> None:
        """Stream.aclose() must call aclose on SSE iterator if available."""
        # Arrange
        stream = ConcreteStream(mock_sse_iterator)

        # Act
        await stream.aclose()

        # Assert - SSE iterator cleanup called
        mock_sse_iterator.aclose.assert_called_once()

    async def test_aclose_handles_sse_iterator_without_aclose(self) -> None:
        """Stream.aclose() must handle SSE iterators without aclose method."""

        # Arrange - Iterator without aclose
        async def simple_iter() -> AsyncIterator[dict[str, Any]]:
            yield {"delta": "test"}

        stream = ConcreteStream(simple_iter())

        # Act & Assert - Should not raise AttributeError
        await stream.aclose()
        assert stream._closed is True

    async def test_aclose_called_on_natural_exhaustion(self) -> None:
        """Stream must call aclose automatically when naturally exhausted."""
        # Arrange
        events = [{"delta": "test"}]
        stream = ConcreteStream(_async_iter(events))

        # Act - Consume stream naturally
        async for _ in stream:
            pass

        # Assert - Stream marked as closed after exhaustion
        assert stream._closed is True


class TestStreamAsyncContextManager:
    """Test Stream AsyncContextManager protocol - cleanup guarantee and exception handling."""

    async def test_context_manager_returns_self(self) -> None:
        """__aenter__ must return Stream instance for iteration."""
        # Arrange
        events = [{"delta": "test"}]
        stream = ConcreteStream(_async_iter(events))

        # Act & Assert
        async with stream as ctx_stream:
            assert ctx_stream is stream

    async def test_context_manager_calls_aclose_on_exit(
        self, mock_sse_iterator: AsyncMock
    ) -> None:
        """__aexit__ must call aclose() to cleanup resources on exit."""
        # Arrange
        stream = ConcreteStream(mock_sse_iterator)

        # Act - Enter and exit context
        async with stream:
            pass

        # Assert - Cleanup called
        assert stream._closed is True
        mock_sse_iterator.aclose.assert_called_once()

    async def test_context_manager_cleanup_on_exception(
        self, mock_sse_iterator: AsyncMock
    ) -> None:
        """__aexit__ must cleanup resources even when exception occurs."""
        # Arrange
        stream = ConcreteStream(mock_sse_iterator)

        # Act & Assert - Exception propagates but cleanup happens
        with pytest.raises(ValueError, match="Test error"):
            async with stream:
                raise ValueError("Test error")

        # Assert - Cleanup happened despite exception
        assert stream._closed is True
        mock_sse_iterator.aclose.assert_called_once()

    async def test_context_manager_propagates_exceptions(self) -> None:
        """__aexit__ must propagate exceptions (returns False)."""
        # Arrange
        events = [{"delta": "test"}]
        stream = ConcreteStream(_async_iter(events))
        exc_type = RuntimeError
        exc_val = RuntimeError("Intentional error")

        # Act & Assert - Exception raised in context must propagate
        with pytest.raises(RuntimeError, match="Intentional error"):
            async with stream:
                raise exc_val

        # Assert - __aexit__ returns False to propagate exceptions
        result = await stream.__aexit__(exc_type, exc_val, None)
        assert result is False

    async def test_context_manager_guarantees_cleanup_on_early_break(self) -> None:
        """Context manager must cleanup when iteration breaks early."""
        # Arrange
        events = [
            {"delta": "first"},
            {"delta": "second"},
            {"delta": "third"},
        ]
        stream = ConcreteStream(_async_iter(events))

        # Act - Break iteration early
        async with stream:
            async for chunk in stream:
                if chunk.content == "first":
                    break  # Early exit

        # Assert - Cleanup still happened
        assert stream._closed is True


class TestStreamAbstractBehavior:
    """Test Stream abstract method enforcement."""

    async def test_cannot_instantiate_base_stream_directly(
        self, mock_sse_iterator: AsyncMock
    ) -> None:
        """Stream must not be instantiable due to abstract methods."""
        # Act & Assert
        with pytest.raises(
            TypeError, match=r"Can't instantiate abstract class.*Stream"
        ) as exc_info:
            Stream(mock_sse_iterator)  # type: ignore[abstract]

        # Verify error mentions missing abstract methods
        error_msg = str(exc_info.value)
        assert "Stream" in error_msg
        assert any(method in error_msg for method in ["_parse_chunk", "_parse_output"])

    async def test_subclass_without_parse_chunk_fails(
        self, mock_sse_iterator: AsyncMock
    ) -> None:
        """Subclass without _parse_chunk implementation must fail instantiation."""

        # Arrange
        class IncompleteStream(Stream[ConcreteOutput]):
            """Missing _parse_chunk implementation."""

            def _parse_output(self, chunks: list[Chunk]) -> ConcreteOutput:
                """Implement _parse_output but not _parse_chunk."""
                return ConcreteOutput(content="test")

        # Act & Assert
        with pytest.raises(TypeError, match=r".*_parse_chunk.*"):
            IncompleteStream(mock_sse_iterator)  # type: ignore[abstract]

    async def test_subclass_without_parse_output_fails(
        self, mock_sse_iterator: AsyncMock
    ) -> None:
        """Subclass without _parse_output implementation must fail instantiation."""

        # Arrange
        class IncompleteStream(Stream[ConcreteOutput]):
            """Missing _parse_output implementation."""

            def _parse_chunk(self, event: dict[str, Any]) -> Chunk | None:
                """Implement _parse_chunk but not _parse_output."""
                return Chunk(content="test")

        # Act & Assert
        with pytest.raises(TypeError, match=r".*_parse_output.*"):
            IncompleteStream(mock_sse_iterator)  # type: ignore[abstract]


class TestStreamRepr:
    """Test Stream.__repr__ method - all state branches."""

    async def test_repr_idle_state(self) -> None:
        """__repr__ must show 'idle' state when stream initialized but no chunks yet."""
        # Arrange
        events: list[dict[str, Any]] = []
        stream = ConcreteStream(_async_iter(events))

        # Act
        repr_str = repr(stream)

        # Assert
        assert "idle" in repr_str
        assert "chunks" not in repr_str
        assert stream.__class__.__name__ in repr_str

    @pytest.mark.parametrize(
        "chunk_count,expected_count",
        [
            (1, "1 chunks"),
            (2, "2 chunks"),
            (3, "3 chunks"),
        ],
    )
    async def test_repr_streaming_state_shows_chunk_count(
        self, chunk_count: int, expected_count: str
    ) -> None:
        """__repr__ must show 'streaming' state with correct chunk count."""
        # Arrange
        events = [{"delta": f"chunk{i}"} for i in range(chunk_count)]
        stream = ConcreteStream(_async_iter(events))

        # Act - Get chunks but don't exhaust stream
        async for _chunk in stream:
            if len(stream._chunks) == chunk_count:
                break  # Stop before exhaustion

        # Assert - State is streaming with correct chunk count
        repr_str = repr(stream)
        assert "streaming" in repr_str
        assert expected_count in repr_str
        assert stream.__class__.__name__ in repr_str

    async def test_repr_closed_state(self) -> None:
        """__repr__ must show 'closed' state when stream closed but no output set."""
        # Arrange
        events = [{"delta": "test"}]
        stream = ConcreteStream(_async_iter(events))

        # Act - Close stream before exhaustion
        await stream.aclose()

        # Assert - State is closed
        repr_str = repr(stream)
        assert "closed" in repr_str
        assert stream.__class__.__name__ in repr_str

    async def test_repr_done_state(self) -> None:
        """__repr__ must show 'done' state when stream exhausted with output set."""
        # Arrange
        events = [{"delta": "test"}]
        stream = ConcreteStream(_async_iter(events))

        # Act - Exhaust stream
        async for _ in stream:
            pass

        # Assert - State is done with chunk count
        repr_str = repr(stream)
        assert "done" in repr_str
        assert "1 chunks" in repr_str
        assert stream.__class__.__name__ in repr_str


class TestStreamEmptyStreamError:
    """Test Stream empty stream error handling."""

    async def test_empty_stream_raises_runtime_error(self) -> None:
        """Stream must raise RuntimeError when exhausted with no chunks."""

        # Arrange - Create stream where all events return None from _parse_chunk
        async def empty_iter() -> AsyncIterator[dict[str, Any]]:
            yield {"type": "ping"}  # Lifecycle event (no delta)
            yield {"finish_reason": "stop"}  # Lifecycle event (no delta)

        stream = ConcreteStream(empty_iter())

        # Act & Assert - Exhaustion raises RuntimeError
        with pytest.raises(
            RuntimeError, match=r"Stream completed but no chunks were produced"
        ):
            async for _ in stream:
                pass

    async def test_stream_with_only_lifecycle_events_raises_error(self) -> None:
        """Stream raises RuntimeError when SSE yields events but all chunks are filtered to None."""
        # Arrange - Events that all return None from _parse_chunk
        events = [
            {"type": "ping"},  # Lifecycle event (no delta/content)
            {"type": "start"},  # Lifecycle event
            {"type": "end"},  # Lifecycle event
            {"finish_reason": "stop"},  # Lifecycle event
        ]
        stream = ConcreteStream(_async_iter(events))

        # Act & Assert - Should raise RuntimeError when exhausted
        with pytest.raises(
            RuntimeError, match=r"Stream completed but no chunks were produced"
        ):
            async for _ in stream:
                pass


class TestStreamExceptionHandling:
    """Test Stream exception handling in __anext__."""

    async def test_anext_handles_exception_in_parse_chunk_and_cleans_up(self) -> None:
        """__anext__ must call aclose() and re-raise when _parse_chunk raises exception."""

        # Arrange - Stream that raises exception in _parse_chunk
        class ExceptionStream(ConcreteStream):
            """Stream that raises exception in _parse_chunk."""

            def _parse_chunk(self, event: dict[str, Any]) -> Chunk | None:
                """Raise exception during parsing."""
                raise ValueError("Parse error")

        events = [{"delta": "test"}]
        stream = ExceptionStream(_async_iter(events))

        # Act & Assert - Exception is re-raised and cleanup happens
        with pytest.raises(ValueError, match="Parse error"):
            await stream.__anext__()

        # Assert - Cleanup was called
        assert stream._closed is True

    async def test_anext_handles_exception_in_parse_output_and_cleans_up(self) -> None:
        """__anext__ must call aclose() and re-raise when _parse_output raises exception."""

        # Arrange - Stream that raises exception in _parse_output
        class ExceptionStream(ConcreteStream):
            """Stream that raises exception in _parse_output."""

            def _parse_output(self, chunks: list[Chunk]) -> ConcreteOutput:
                """Raise exception during output parsing."""
                raise RuntimeError("Output parse error")

        events = [{"delta": "test"}]
        stream = ExceptionStream(_async_iter(events))

        # Act & Assert - Exception is re-raised and cleanup happens
        with pytest.raises(RuntimeError, match="Output parse error"):
            async for _ in stream:
                pass

        # Assert - Cleanup was called
        assert stream._closed is True

    async def test_anext_handles_exception_in_sse_iterator_and_cleans_up(self) -> None:
        """__anext__ must call aclose() and re-raise when SSE iterator raises exception."""

        # Arrange - SSE iterator that raises exception
        async def failing_iter() -> AsyncIterator[dict[str, Any]]:
            """Iterator that raises exception."""
            yield {"delta": "test"}
            raise ConnectionError("Connection lost")

        stream = ConcreteStream(failing_iter())

        # Act & Assert - Exception is re-raised and cleanup happens
        with pytest.raises(ConnectionError, match="Connection lost"):
            async for chunk in stream:
                # First chunk succeeds
                assert chunk.content == "test"
                # Next iteration will raise exception
                await stream.__anext__()

        # Assert - Cleanup was called
        assert stream._closed is True


class TestStreamWithTypedUsageAndFinishReason:
    """Test Stream with capability-specific Usage and FinishReason subclasses.

    Validates that the hierarchical pattern works with actual fields
    before migrating existing packages (CEL-39).
    """

    async def test_typed_usage_and_finish_reason_in_chunks(self) -> None:
        """Stream must support capability-specific Usage/FinishReason with actual fields."""

        # Arrange - Define typed Usage and FinishReason with fields
        class TypedUsage(Usage):
            """Typed usage with actual fields."""

            input_tokens: int
            output_tokens: int

        class TypedFinishReason(FinishReason):
            """Typed finish reason with actual field."""

            reason: str

        class TypedChunk(Chunk[str]):
            """Typed chunk with specific finish_reason and usage."""

            finish_reason: TypedFinishReason | None = None
            usage: TypedUsage | None = None

        class TypedOutput(Output[str]):
            """Typed output with specific usage."""

            usage: TypedUsage = Field(
                default_factory=lambda: TypedUsage(input_tokens=0, output_tokens=0)
            )

        class TypedStream(Stream[TypedOutput]):
            """Stream using typed classes."""

            def _parse_chunk(self, event: dict[str, Any]) -> TypedChunk | None:
                """Parse event to typed chunk."""
                content = event.get("delta")
                if not content:
                    return None

                # Build typed finish_reason if present
                finish_reason = None
                if "finish_reason" in event:
                    finish_reason = TypedFinishReason(reason=event["finish_reason"])

                # Build typed usage if present
                usage = None
                if "usage" in event:
                    usage = TypedUsage(
                        input_tokens=event["usage"]["input_tokens"],
                        output_tokens=event["usage"]["output_tokens"],
                    )

                return TypedChunk(
                    content=content,
                    finish_reason=finish_reason,
                    usage=usage,
                )

            def _parse_output(self, chunks: list[Chunk]) -> TypedOutput:
                """Combine chunks into typed output."""
                content = "".join(chunk.content for chunk in chunks)

                # Extract usage from final chunk (typed)
                final_chunk = chunks[-1] if chunks else None
                usage = (
                    final_chunk.usage
                    if final_chunk and isinstance(final_chunk.usage, TypedUsage)
                    else TypedUsage(input_tokens=0, output_tokens=0)
                )

                return TypedOutput(content=content, usage=usage)

        # Act - Stream with typed chunks
        events: list[dict[str, Any]] = [
            {"delta": "Hello"},
            {"delta": " world"},
            {
                "delta": "!",
                "finish_reason": "stop",
                "usage": {"input_tokens": 5, "output_tokens": 10},
            },
        ]
        stream = TypedStream(_async_iter(events))

        chunks = [chunk async for chunk in stream]

        # Assert - Chunks have typed finish_reason and usage
        assert len(chunks) == 3
        assert chunks[0].finish_reason is None
        assert chunks[0].usage is None

        assert chunks[2].finish_reason is not None
        assert isinstance(chunks[2].finish_reason, TypedFinishReason)
        assert chunks[2].finish_reason.reason == "stop"
        assert chunks[2].usage is not None
        assert isinstance(chunks[2].usage, TypedUsage)
        assert chunks[2].usage.input_tokens == 5
        assert chunks[2].usage.output_tokens == 10

        # Assert - Output has typed usage
        output = stream.output
        assert output.content == "Hello world!"
        assert isinstance(output.usage, TypedUsage)
        assert output.usage.input_tokens == 5
        assert output.usage.output_tokens == 10
