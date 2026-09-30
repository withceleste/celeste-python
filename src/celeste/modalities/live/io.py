"""IO types for live modality."""

from pydantic import Field

from celeste.artifacts import AudioArtifact
from celeste.io import Chunk, FinishReason, Input, Output, Usage
from celeste.tools import ToolCall, ToolResult
from celeste.types import Message


class LiveInput(Input):
    """Conversation context supplied when connecting."""

    messages: list[Message | ToolResult] | None = None


class LiveFinishReason(FinishReason):
    """Live finish reason."""

    reason: str | None = None
    message: str | None = None


class LiveUsage(Usage):
    """Live usage metrics."""

    total_tokens: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None
    cached_tokens: int | None = None
    billed_units: float | None = None


class LiveOutput(Output[AudioArtifact]):
    """Output with the model's audio and the conversation exchanged during the livestream."""

    usage: LiveUsage = Field(default_factory=LiveUsage)
    finish_reason: LiveFinishReason | None = None
    messages: list[Message | ToolResult] = Field(default_factory=list)


class LiveChunk(Chunk[bytes]):
    """Chunk for live streaming: raw model audio plus transcripts and tool calls."""

    finish_reason: LiveFinishReason | None = None
    usage: LiveUsage | None = None
    transcript: Message | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)


__all__ = [
    "LiveChunk",
    "LiveFinishReason",
    "LiveInput",
    "LiveOutput",
    "LiveUsage",
]
