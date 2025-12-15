"""BytePlus provider for video generation."""

from celeste.core import Provider

from .client import BytePlusVideoGenerationClient

__all__ = ["PROVIDERS", "BytePlusVideoGenerationClient"]

PROVIDERS: list[tuple[Provider, type[BytePlusVideoGenerationClient]]] = [
    (Provider.BYTEPLUS, BytePlusVideoGenerationClient),
]
