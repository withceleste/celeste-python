"""Input and output types for music generation."""

from celeste.artifacts import AudioArtifact
from celeste.io import Chunk, FinishReason, Input, Output, Usage


class MusicGenerationInput(Input):
    """Input for music generation operations."""

    prompt: str


class MusicGenerationFinishReason(FinishReason):
    """Music generation finish reason.

    Stores raw provider reason. Providers map their values in implementation.
    """

    reason: str
    message: str | None = None


class MusicGenerationUsage(Usage):
    """Music generation usage metrics.

    All fields optional since providers vary.
    """

    total_tokens: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    generated_duration: float | None = None
    billed_units: float | None = None
    credits_used: float | None = None


class MusicGenerationOutput(Output[AudioArtifact]):
    """Output with AudioArtifact content."""

    pass


class MusicGenerationChunk(Chunk[AudioArtifact]):
    """Typed chunk for music generation streaming.

    For async task-based providers (like Mureka), chunks represent
    progressive updates: task status, partial results, or final audio.
    """

    finish_reason: MusicGenerationFinishReason | None = None
    usage: MusicGenerationUsage | None = None
    task_status: str | None = None  # e.g., "pending", "streaming", "succeeded"


__all__ = [
    "MusicGenerationChunk",
    "MusicGenerationFinishReason",
    "MusicGenerationInput",
    "MusicGenerationOutput",
    "MusicGenerationUsage",
]
