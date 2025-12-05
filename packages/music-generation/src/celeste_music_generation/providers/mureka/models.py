"""Mureka models for music generation."""

from celeste import Model, Provider
from celeste.constraints import Range
from celeste_music_generation.constraints import DURATION_RANGE, QUALITY_CHOICES
from celeste_music_generation.parameters import MusicGenerationParameter

MODELS: list[Model] = [
    Model(
        id="mureka-v1",
        provider=Provider.MUREKA,
        display_name="Mureka V1",
        streaming=True,
        parameter_constraints={
            MusicGenerationParameter.DURATION: DURATION_RANGE,
            MusicGenerationParameter.QUALITY: QUALITY_CHOICES,
        },
    ),
    Model(
        id="mureka-o1",
        provider=Provider.MUREKA,
        display_name="Mureka O1",
        streaming=False,  # mureka-o1 does not support streaming
        parameter_constraints={
            MusicGenerationParameter.DURATION: Range(min=5, max=180),  # Up to 3 min
            MusicGenerationParameter.QUALITY: QUALITY_CHOICES,
        },
    ),
]

__all__ = ["MODELS"]
