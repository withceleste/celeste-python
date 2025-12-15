"""ByteDance provider for video generation."""

from celeste.core import Provider

from .client import ByteDanceVideoGenerationClient

__all__ = ["PROVIDERS", "ByteDanceVideoGenerationClient"]

PROVIDERS: list[tuple[Provider, type[ByteDanceVideoGenerationClient]]] = [
    (Provider.BYTEDANCE, ByteDanceVideoGenerationClient),
]
