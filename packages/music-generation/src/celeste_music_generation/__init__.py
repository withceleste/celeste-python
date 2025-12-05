"""Celeste music generation capability."""


def register_package() -> None:
    """Register music generation package (client and models)."""
    from celeste.client import register_client
    from celeste.core import Capability
    from celeste.models import register_models
    from celeste_music_generation.models import MODELS
    from celeste_music_generation.providers import PROVIDERS

    for provider, client_class in PROVIDERS:
        register_client(Capability.MUSIC_GENERATION, provider, client_class)

    register_models(MODELS, capability=Capability.MUSIC_GENERATION)


from celeste_music_generation.io import (  # noqa: E402
    MusicGenerationChunk,
    MusicGenerationFinishReason,
    MusicGenerationInput,
    MusicGenerationOutput,
    MusicGenerationUsage,
)
from celeste_music_generation.streaming import MusicGenerationStream  # noqa: E402

__all__ = [
    "MusicGenerationChunk",
    "MusicGenerationFinishReason",
    "MusicGenerationInput",
    "MusicGenerationOutput",
    "MusicGenerationStream",
    "MusicGenerationUsage",
    "register_package",
]
