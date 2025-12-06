"""Parameters for audio recognition."""

from enum import StrEnum

from celeste.parameters import Parameters


class AudioRecognitionParameter(StrEnum):
    """Parameters for audio recognition operations."""

    INPUT_FORMAT = "input_format"
    LANGUAGE = "language"


class AudioRecognitionParameters(Parameters):
    """Type-safe parameters for audio recognition.

    Attributes:
        input_format: Audio input format (pcm, wav, opus, etc.)
        language: Optional language hint for transcription
    """

    input_format: str | None = None
    language: str | None = None


__all__ = [
    "AudioRecognitionParameter",
    "AudioRecognitionParameters",
]
