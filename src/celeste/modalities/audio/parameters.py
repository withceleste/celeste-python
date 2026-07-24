"""Parameters for audio modality."""

from enum import StrEnum
from typing import Annotated

from pydantic import Field

from celeste.artifacts import ImageArtifact
from celeste.parameters import Parameters


class AudioParameter(StrEnum):
    """Unified parameter names for audio modality."""

    VOICE = "voice"
    SPEED = "speed"
    OUTPUT_FORMAT = "output_format"
    LANGUAGE = "language"
    REFERENCE_IMAGES = "reference_images"
    PROMPT = "prompt"
    TEMPERATURE = "temperature"
    AUDIO = "audio"


class AudioParameters(Parameters, total=False):
    """Parameters for audio operations."""

    voice: Annotated[
        str, Field(description="Voice identifier for text-to-speech output.")
    ]
    speed: Annotated[
        float, Field(description="Playback speed multiplier (1.0 = normal).")
    ]
    output_format: Annotated[str, Field(description="Audio file format.")]
    language: Annotated[
        str,
        Field(description="Language tag (ISO-639-1 for transcription, e.g. 'en')."),
    ]
    reference_images: Annotated[
        list[ImageArtifact],
        Field(description="Additional images conditioning the audio."),
    ]
    temperature: Annotated[
        float,
        Field(description="Sampling temperature for transcription (0-1)."),
    ]


__all__ = [
    "AudioParameter",
    "AudioParameters",
]
