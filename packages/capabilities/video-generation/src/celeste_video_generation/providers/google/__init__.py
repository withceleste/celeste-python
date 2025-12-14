"""Google provider for video generation."""

from celeste.core import Provider
from celeste_video_generation.providers.google.client import GoogleVideoGenerationClient

__all__ = ["PROVIDERS", "GoogleVideoGenerationClient"]

PROVIDERS: list[tuple[Provider, type[GoogleVideoGenerationClient]]] = [
    (Provider.GOOGLE, GoogleVideoGenerationClient),
]
