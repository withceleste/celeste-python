"""Parameters for audio modality."""

from enum import StrEnum
from typing import Annotated

from pydantic import Field

from celeste.parameters import Parameters


class AudioParameter(StrEnum):
    """Unified parameter names for audio modality."""

    VOICE = "voice"
    SPEED = "speed"
    OUTPUT_FORMAT = "output_format"
    PROMPT = "prompt"
    LANGUAGE = "language"


class AudioParameters(Parameters, total=False):
    """Parameters for audio operations."""

    voice: Annotated[
        str, Field(description="Voice identifier for text-to-speech output.")
    ]
    speed: Annotated[
        float, Field(description="Playback speed multiplier (1.0 = normal).")
    ]
    output_format: Annotated[str, Field(description="Audio file format.")]
    prompt: Annotated[
        str, Field(description="Style or delivery instruction for the voice.")
    ]
    language: Annotated[str, Field(description="BCP-47 language tag, e.g. 'en-US'.")]


__all__ = [
    "AudioParameter",
    "AudioParameters",
]
