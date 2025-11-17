"""OpenAI provider for video generation."""

from celeste.core import Provider
from celeste_video_generation.providers.openai.client import OpenAIVideoGenerationClient

__all__ = ["PROVIDERS", "OpenAIVideoGenerationClient"]

PROVIDERS: list[tuple[Provider, type[OpenAIVideoGenerationClient]]] = [
    (Provider.OPENAI, OpenAIVideoGenerationClient),
]
