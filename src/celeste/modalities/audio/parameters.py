"""Parameters for audio modality."""

from enum import StrEnum

from celeste.parameters import Parameters


class AudioParameter(StrEnum):
    """Unified parameter names for audio modality."""

    VOICE = "voice"
    SPEED = "speed"
    OUTPUT_FORMAT = "output_format"
    PROMPT = "prompt"
    LANGUAGE = "language"


class AudioParameters(Parameters):
    """Parameters for audio operations."""

    voice: str
    speed: float
    output_format: str
    prompt: str
    language: str


__all__ = [
    "AudioParameter",
    "AudioParameters",
]
