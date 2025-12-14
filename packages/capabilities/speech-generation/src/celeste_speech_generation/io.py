"""Input and output types for speech generation."""

from celeste.artifacts import AudioArtifact
from celeste.io import Chunk, Input, Output, Usage


class SpeechGenerationInput(Input):
    """Input for speech generation operations."""

    text: str


class SpeechGenerationUsage(Usage):
    """Speech generation usage metrics.

    All fields optional since providers vary.
    """


class SpeechGenerationOutput(Output[AudioArtifact]):
    """Output with audio artifact content."""


class SpeechGenerationChunk(Chunk[bytes]):
    """Typed chunk for speech generation streaming.

    Note: Unlike TextGenerationChunk, this class intentionally omits a finish_reason
    field. TTS providers stream raw audio bytes without completion signals - the
    stream simply ends when audio generation is complete.
    """

    usage: SpeechGenerationUsage | None = None


__all__ = [
    "SpeechGenerationChunk",
    "SpeechGenerationInput",
    "SpeechGenerationOutput",
    "SpeechGenerationUsage",
]
