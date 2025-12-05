"""Mureka models for music generation."""

from celeste import Model, Provider
from celeste.constraints import Range, Str
from celeste_music_generation.parameters import MusicGenerationParameter

# Lyrics constraint: max 3000 characters according to Mureka docs
LYRICS_CONSTRAINT = Str(min_length=1, max_length=3000)

MODELS: list[Model] = [
    Model(
        id="auto",
        provider=Provider.MUREKA,
        display_name="Mureka Auto",
        streaming=True,
        parameter_constraints={
            MusicGenerationParameter.LYRICS: LYRICS_CONSTRAINT,
            MusicGenerationParameter.N: Range(min=1, max=3),
        },
    ),
    Model(
        id="mureka-6",
        provider=Provider.MUREKA,
        display_name="Mureka 6",
        streaming=True,
        parameter_constraints={
            MusicGenerationParameter.LYRICS: LYRICS_CONSTRAINT,
            MusicGenerationParameter.N: Range(min=1, max=3),
        },
    ),
    Model(
        id="mureka-7.5",
        provider=Provider.MUREKA,
        display_name="Mureka 7.5",
        streaming=True,
        parameter_constraints={
            MusicGenerationParameter.LYRICS: LYRICS_CONSTRAINT,
            MusicGenerationParameter.N: Range(min=1, max=3),
        },
    ),
    Model(
        id="mureka-o1",
        provider=Provider.MUREKA,
        display_name="Mureka O1",
        streaming=False,  # mureka-o1 does not support streaming
        parameter_constraints={
            MusicGenerationParameter.LYRICS: LYRICS_CONSTRAINT,
            MusicGenerationParameter.N: Range(min=1, max=3),
        },
    ),
]

__all__ = ["MODELS"]
