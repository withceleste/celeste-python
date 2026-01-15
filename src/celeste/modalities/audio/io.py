"""Input and output types for audio modality."""

from pydantic import Field

from celeste.artifacts import AudioArtifact
from celeste.io import Chunk, FinishReason, Input, Output, Usage


class AudioInput(Input):
    """Input for audio operations."""

    text: str


class AudioFinishReason(FinishReason):
    """Audio finish reason."""

    reason: str | None = None
    message: str | None = None


class AudioUsage(Usage):
    """Audio usage metrics.

    All fields optional since providers vary.
    """


class AudioOutput(Output[AudioArtifact]):
    """Output with audio artifact content."""

    usage: AudioUsage = Field(default_factory=AudioUsage)
    finish_reason: AudioFinishReason | None = None


class AudioChunk(Chunk[bytes]):
    """Typed chunk for audio streaming.

    Audio streaming sends raw bytes without finish_reason.
    """

    usage: AudioUsage | None = None


__all__ = [
    "AudioChunk",
    "AudioFinishReason",
    "AudioInput",
    "AudioOutput",
    "AudioUsage",
]
