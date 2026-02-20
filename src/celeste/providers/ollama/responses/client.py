"""Ollama API client (Responses API protocol)."""

from celeste.protocols.openresponses.client import OpenResponsesClient
from celeste.protocols.openresponses.streaming import OpenResponsesStream

from .config import DEFAULT_BASE_URL

# Re-export with Ollama naming
OllamaClient = OpenResponsesClient
OllamaStream = OpenResponsesStream

__all__ = ["DEFAULT_BASE_URL", "OllamaClient", "OllamaStream"]
