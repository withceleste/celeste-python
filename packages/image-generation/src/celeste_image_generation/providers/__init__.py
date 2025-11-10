"""Provider implementations for image generation."""

from celeste import Client, Provider

__all__ = ["PROVIDERS"]


def _get_providers() -> list[tuple[Provider, type[Client]]]:
    """Lazy-load providers."""
    # Import clients directly from .client modules to avoid __init__.py imports
    from celeste_image_generation.providers.bytedance.client import (
        ByteDanceImageGenerationClient,
    )
    from celeste_image_generation.providers.google.client import (
        GoogleImageGenerationClient,
    )
    from celeste_image_generation.providers.openai.client import (
        OpenAIImageGenerationClient,
    )

    return [
        (Provider.BYTEDANCE, ByteDanceImageGenerationClient),
        (Provider.GOOGLE, GoogleImageGenerationClient),
        (Provider.OPENAI, OpenAIImageGenerationClient),
    ]


PROVIDERS: list[tuple[Provider, type[Client]]] = _get_providers()
