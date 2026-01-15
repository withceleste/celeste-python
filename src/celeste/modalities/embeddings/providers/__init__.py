"""Embeddings providers."""

from celeste.core import Provider

from ..client import EmbeddingsClient
from .google import GoogleEmbeddingsClient

PROVIDERS: dict[Provider, type[EmbeddingsClient]] = {
    Provider.GOOGLE: GoogleEmbeddingsClient,
}
