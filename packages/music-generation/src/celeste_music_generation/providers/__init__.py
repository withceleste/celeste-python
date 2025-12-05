"""Provider implementations for music generation."""

from celeste import Client, Provider

__all__ = ["PROVIDERS"]


def _get_providers() -> list[tuple[Provider, type[Client]]]:
    """Lazy-load providers."""
    # Import clients directly from .client modules to avoid __init__.py imports
    from celeste_music_generation.providers.mureka.client import (
        MurekaMusicGenerationClient,
    )

    return [
        (Provider.MUREKA, MurekaMusicGenerationClient),
    ]


PROVIDERS: list[tuple[Provider, type[Client]]] = _get_providers()
