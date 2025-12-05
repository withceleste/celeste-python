"""Model definitions for music generation."""

from celeste import Model
from celeste_music_generation.providers.mureka.models import MODELS as MUREKA_MODELS

MODELS: list[Model] = [
    *MUREKA_MODELS,
]

__all__ = ["MODELS"]
