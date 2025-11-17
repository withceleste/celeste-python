"""Provider implementations for video generation."""

from celeste import Client, Provider

__all__ = ["PROVIDERS"]


def _get_providers() -> list[tuple[Provider, type[Client]]]:
    """Lazy-load providers."""
    # Import clients directly from .client modules to avoid __init__.py imports
    from celeste_video_generation.providers.bytedance.client import (
        ByteDanceVideoGenerationClient,
    )
    from celeste_video_generation.providers.google.client import (
        GoogleVideoGenerationClient,
    )
    from celeste_video_generation.providers.openai.client import (
        OpenAIVideoGenerationClient,
    )

    return [
        (Provider.BYTEDANCE, ByteDanceVideoGenerationClient),
        (Provider.GOOGLE, GoogleVideoGenerationClient),
        (Provider.OPENAI, OpenAIVideoGenerationClient),
    ]


PROVIDERS: list[tuple[Provider, type[Client]]] = _get_providers()
