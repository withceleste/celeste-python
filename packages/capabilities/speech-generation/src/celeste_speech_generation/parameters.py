"""Parameters for speech generation."""

from enum import StrEnum

from celeste.parameters import Parameters


class SpeechGenerationParameter(StrEnum):
    """Unified parameter names for speech generation capability."""

    VOICE = "voice"
    SPEED = "speed"
    OUTPUT_FORMAT = "output_format"
    PROMPT = "prompt"
    LANGUAGE = "language"


class SpeechGenerationParameters(Parameters):
    """Parameters for speech generation."""

    voice: str | None
    speed: float | None
    output_format: str | None
    prompt: str | None
