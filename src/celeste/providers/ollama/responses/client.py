"""Ollama API client (OpenResponses protocol)."""

from celeste.providers.openresponses.responses.client import OpenResponsesClient
from celeste.providers.openresponses.responses.streaming import OpenResponsesStream

from .config import DEFAULT_BASE_URL


class OllamaClient(OpenResponsesClient):
    """Ollama API client mixin (OpenResponses protocol)."""

    pass


# Re-export stream class
OllamaStream = OpenResponsesStream

__all__ = ["DEFAULT_BASE_URL", "OllamaClient", "OllamaStream"]
