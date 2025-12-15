"""Input and output types for speech generation."""

from celeste.artifacts import AudioArtifact
from celeste.io import Chunk, FinishReason, Input, Output, Usage


class SpeechGenerationInput(Input):
    """Input for speech generation operations."""

    text: str


class SpeechGenerationUsage(Usage):
    """Speech generation usage metrics.

    All fields optional since providers vary.
    """


class SpeechGenerationFinishReason(FinishReason):
    """Finish reason for speech generation."""


class SpeechGenerationOutput(Output[AudioArtifact]):
    """Output with audio artifact content."""


class SpeechGenerationChunk(Chunk[bytes]):
    """Typed chunk for speech generation streaming.

    Speech streaming sends raw bytes without finish_reason.
    """

    usage: SpeechGenerationUsage | None = None


__all__ = [
    "SpeechGenerationChunk",
    "SpeechGenerationFinishReason",
    "SpeechGenerationInput",
    "SpeechGenerationOutput",
    "SpeechGenerationUsage",
]
