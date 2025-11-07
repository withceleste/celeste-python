"""Celeste text generation capability."""




def register_package() -> None:
    """Register text generation package (client and models)."""
    from celeste.core import Capability
    from celeste.client import register_client
    from celeste.models import register_models
    from celeste_text_generation.models import MODELS
    from celeste_text_generation.providers import PROVIDERS

    # Register provider-specific clients
    for provider, client_class in PROVIDERS:
        register_client(Capability.TEXT_GENERATION, provider, client_class)

    register_models(MODELS, capability=Capability.TEXT_GENERATION)


# Import after register_package is defined to avoid circular imports
from celeste_text_generation.io import (
    TextGenerationInput,
    TextGenerationOutput,
    TextGenerationUsage,
)
from celeste_text_generation.streaming import TextGenerationStream

__all__ = [
    "TextGenerationInput",
    "TextGenerationOutput",
    "TextGenerationStream",
    "TextGenerationUsage",
    "register_package",
]
