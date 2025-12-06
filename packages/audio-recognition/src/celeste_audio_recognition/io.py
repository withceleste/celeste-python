"""Input/Output types for audio recognition."""

from celeste.io import Chunk, Input, Output, Usage


class AudioRecognitionInput(Input):
    """Input for audio recognition operations.

    Attributes:
        audio: Raw audio data as bytes
        format: Audio format (pcm, wav, opus, etc.)
    """

    audio: bytes
    format: str = "pcm"


class AudioRecognitionUsage(Usage):
    """Usage metrics for audio recognition.

    Attributes:
        characters: Number of characters transcribed
        duration_s: Duration of audio processed in seconds
    """

    characters: int | None = None
    duration_s: float | None = None


class AudioRecognitionOutput[Content](Output[Content]):
    """Output from audio recognition operations.

    Content is transcribed text (str).
    """

    pass


class AudioRecognitionChunk(Chunk[str]):
    """Typed chunk for audio recognition streaming.

    Content is incremental text transcription.
    Chunks are emitted as audio is transcribed in real-time.
    """

    usage: AudioRecognitionUsage | None = None
    # Additional metadata for VAD and timing
    start_s: float | None = None
    stop_s: float | None = None
    stream_id: int | None = None


__all__ = [
    "AudioRecognitionChunk",
    "AudioRecognitionInput",
    "AudioRecognitionOutput",
    "AudioRecognitionUsage",
]
