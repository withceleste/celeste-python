"""Celeste image generation capability."""


def register_package() -> None:
    """Register image generation package (client and models)."""
    from celeste.client import register_client
    from celeste.core import Capability
    from celeste.models import register_models
    from celeste_image_generation.models import MODELS
    from celeste_image_generation.providers import PROVIDERS

    for provider, client_class in PROVIDERS:
        register_client(Capability.IMAGE_GENERATION, provider, client_class)

    register_models(MODELS, capability=Capability.IMAGE_GENERATION)


from celeste_image_generation.io import (  # noqa: E402
    ImageGenerationChunk,
    ImageGenerationFinishReason,
    ImageGenerationInput,
    ImageGenerationOutput,
    ImageGenerationUsage,
)
from celeste_image_generation.streaming import ImageGenerationStream  # noqa: E402

__all__ = [
    "ImageGenerationChunk",
    "ImageGenerationFinishReason",
    "ImageGenerationInput",
    "ImageGenerationOutput",
    "ImageGenerationStream",
    "ImageGenerationUsage",
    "register_package",
]
