"""Live streaming primitives."""

import asyncio
import json
from abc import abstractmethod
from typing import Any, Unpack

from celeste.artifacts import AudioArtifact, ImageArtifact
from celeste.streaming import Stream
from celeste.tools import ToolCall, ToolResult
from celeste.types import Message, Role

from .io import (
    LiveChunk,
    LiveFinishReason,
    LiveOutput,
    LiveUsage,
)
from .parameters import LiveParameters


class LiveStream(Stream[LiveOutput, LiveParameters, LiveChunk]):
    """Streaming for live modality, with a send side for the bidirectional session."""

    _usage_class = LiveUsage
    _finish_reason_class = LiveFinishReason
    _chunk_class = LiveChunk
    _output_class = LiveOutput
    _empty_content = b""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs)
        # ponytail: unbounded; bound it if senders outrun the socket.
        self._outbound: asyncio.Queue[str | None] = asyncio.Queue()
        self._messages: list[Message | ToolResult] = []
        self._last_transcript: Message | None = None
        self._ended = False

    async def send(
        self,
        item: str
        | Message
        | ToolResult
        | AudioArtifact
        | ImageArtifact
        | dict[str, Any],
    ) -> None:
        """Queue one input in order; the transport sends it once connected."""
        if self._closed or self._ended:
            raise RuntimeError("Livestream has ended")
        if isinstance(item, str):
            item = Message(role=Role.USER, content=item)
        if isinstance(item, dict):
            frames = [item]
        elif isinstance(item, Message):
            frames = self._serialize_message(item)
        elif isinstance(item, ToolResult):
            frames = self._serialize_tool_result(item)
        elif isinstance(item, AudioArtifact):
            frames = self._serialize_audio(item)
        elif isinstance(item, ImageArtifact):
            frames = self._serialize_image(item)
        else:
            raise TypeError(f"Cannot send {type(item).__name__} on a livestream")
        encoded = [json.dumps(frame) for frame in frames]
        if isinstance(item, Message | ToolResult):
            self._messages.append(item)
        for frame in encoded:
            self._outbound.put_nowait(frame)

    async def end(self) -> None:
        """Stop sending; the livestream then ends when the provider finishes."""
        if not self._ended:
            self._ended = True
            self._outbound.put_nowait(None)

    def _parse_chunk(self, event: dict[str, Any]) -> LiveChunk | None:
        """Lend the outbound queue to the transport, then yield every server event."""
        if "outbound" in event:
            event["outbound"] = self._outbound
            return None
        chunk = super()._parse_chunk(event) or LiveChunk(
            content=self._empty_content, metadata={"event_data": event}
        )
        self._record(chunk)
        return chunk

    def _record(self, chunk: LiveChunk) -> None:
        """Merge transcript fragments per speaker and append tool calls to the conversation."""
        transcript = chunk.transcript
        last = self._last_transcript
        if transcript is not None:
            if (
                last is not None
                and self._messages
                and self._messages[-1] is last
                and last.role == transcript.role
                and isinstance(last.content, str)
                and isinstance(transcript.content, str)
            ):
                last.content += transcript.content
            else:
                self._last_transcript = transcript.model_copy()
                self._messages.append(self._last_transcript)
        if chunk.tool_calls:
            self._messages.append(
                Message(role=Role.ASSISTANT, content="", tool_calls=chunk.tool_calls)
            )
        if chunk.finish_reason is not None:
            self._last_transcript = None

    def _serialize_message(self, message: Message) -> list[dict[str, Any]]:
        """Serialize a conversational message where the wire supports it."""
        raise NotImplementedError(f"{type(self).__name__} cannot send messages")

    def _serialize_tool_result(self, result: ToolResult) -> list[dict[str, Any]]:
        """Serialize an application-provided tool result."""
        raise NotImplementedError(f"{type(self).__name__} cannot send tool results")

    def _serialize_audio(self, audio: AudioArtifact) -> list[dict[str, Any]]:
        """Serialize declared raw audio without transcoding."""
        raise NotImplementedError(f"{type(self).__name__} cannot send audio")

    def _serialize_image(self, image: ImageArtifact) -> list[dict[str, Any]]:
        """Serialize one image frame."""
        raise NotImplementedError(f"{type(self).__name__} cannot send images")

    def _aggregate_tool_calls(
        self, chunks: list[LiveChunk], raw_events: list[dict[str, Any]]
    ) -> list[ToolCall]:
        """Rebuild tool calls from raw events so the output validates them once."""
        return [
            call for event in raw_events for call in self._parse_chunk_tool_calls(event)
        ]

    def _parse_output(
        self,
        chunks: list[LiveChunk],
        **parameters: Unpack[LiveParameters],
    ) -> LiveOutput:
        """Parse the final Output and attach the conversation sent and received."""
        output = super()._parse_output(chunks, **parameters)
        return output.model_copy(update={"messages": list(self._messages)})

    @abstractmethod
    def _aggregate_content(self, chunks: list[LiveChunk]) -> AudioArtifact:
        """Aggregate audio bytes from chunks into AudioArtifact."""
        ...


__all__ = ["LiveStream"]
