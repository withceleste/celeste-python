"""Parameters for live modality."""

from enum import StrEnum
from typing import Annotated, TypedDict

from pydantic import Field

from celeste.artifacts import ImageArtifact
from celeste.mime_types import AudioMimeType
from celeste.parameters import Parameters
from celeste.tools import ToolDefinition


class LiveParameter(StrEnum):
    """Unified parameter names for live modality."""

    TEMPERATURE = "temperature"
    MAX_TOKENS = "max_tokens"
    SEED = "seed"
    VOICE = "voice"
    AUDIO_FORMAT = "audio_format"
    TOOLS = "tools"
    THINKING_LEVEL = "thinking_level"
    REFERENCE_IMAGES = "reference_images"
    AUDIO = "audio"
    IMAGE = "image"


class LiveAudioFormat(TypedDict):
    """Raw audio encoding and sample rate negotiated at startup."""

    type: AudioMimeType
    rate: int


class LiveParameters(Parameters, total=False):
    """Parameters for live operations."""

    voice: Annotated[str, Field(description="Session output voice.")]
    audio_format: Annotated[
        str | LiveAudioFormat,
        Field(description="Shared raw input/output audio encoding and sample rate."),
    ]
    tools: Annotated[
        list[ToolDefinition],
        Field(description="Tools the model may call during the session."),
    ]
    thinking_level: Annotated[str, Field(description="Model reasoning depth.")]
    reference_images: Annotated[
        list[ImageArtifact],
        Field(description="Images seeded into the session context."),
    ]
    temperature: Annotated[
        float, Field(description="Sampling randomness; 0.0 is deterministic.")
    ]
    max_tokens: Annotated[int, Field(description="Maximum tokens to generate.")]
    seed: Annotated[int, Field(description="Seed for deterministic output.")]


__all__ = ["LiveAudioFormat", "LiveParameter", "LiveParameters"]
