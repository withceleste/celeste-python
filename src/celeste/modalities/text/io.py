"""IO types for text modality.

Text modality handles:
- Text generation (prompt → text)
- Analysis of any media type (text/image/video/audio + prompt → text)

Types are unified per-modality since generate and analyze produce identical outputs.
"""

from pydantic import Field

from celeste.io import Chunk, FinishReason, Input, Output, Usage
from celeste.types import AudioContent, ImageContent, Message, TextContent, VideoContent


class TextInput(Input):
    """Input for text operations."""

    prompt: str | None = None
    messages: list[Message] | None = None
    text: str | list[str] | None = None
    image: ImageContent | None = None
    video: VideoContent | None = None
    audio: AudioContent | None = None


class TextFinishReason(FinishReason):
    """Text finish reason."""

    reason: str | None = None
    message: str | None = None


class TextUsage(Usage):
    """Text usage metrics."""

    total_tokens: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None


class TextOutput(Output[TextContent]):
    """Output from text operations."""

    usage: TextUsage = Field(default_factory=TextUsage)
    finish_reason: TextFinishReason | None = None


class TextChunk(Chunk[str]):
    """Chunk for text streaming."""

    finish_reason: TextFinishReason | None = None
    usage: TextUsage | None = None


__all__ = [
    "TextChunk",
    "TextFinishReason",
    "TextInput",
    "TextOutput",
    "TextUsage",
]
