"""Parameters for speech generation."""

from enum import StrEnum

from celeste.parameters import Parameters


class SpeechGenerationParameter(StrEnum):
    """Unified parameter names for speech generation capability."""

    VOICE = "voice"
    SPEED = "speed"
    RESPONSE_FORMAT = "response_format"
    PROMPT = "prompt"


class SpeechGenerationParameters(Parameters):
    """Parameters for speech generation."""

    voice: str | None
    speed: float | None
    response_format: str | None
    prompt: str | None
