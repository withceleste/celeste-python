"""Celeste text generation capability."""


def register_package() -> None:
    """Register text generation package (client and models)."""
    from celeste.client import register_client
    from celeste.core import Capability
    from celeste.models import register_models
    from celeste_text_generation.models import MODELS
    from celeste_text_generation.providers import PROVIDERS

    for provider, client_class in PROVIDERS:
        register_client(Capability.TEXT_GENERATION, provider, client_class)

    register_models(MODELS, capability=Capability.TEXT_GENERATION)


from celeste_text_generation.io import (  # noqa: E402
    TextGenerationChunk,
    TextGenerationFinishReason,
    TextGenerationInput,
    TextGenerationOutput,
    TextGenerationUsage,
)
from celeste_text_generation.streaming import TextGenerationStream  # noqa: E402

__all__ = [
    "TextGenerationChunk",
    "TextGenerationFinishReason",
    "TextGenerationInput",
    "TextGenerationOutput",
    "TextGenerationStream",
    "TextGenerationUsage",
    "register_package",
]
