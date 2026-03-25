"""Ollama text client (OpenResponses protocol)."""

from typing import ClassVar

from celeste.modalities.text.protocols.openresponses.client import (
    OpenResponsesTextClient,
    OpenResponsesTextStream,
)
from celeste.providers.ollama.responses.config import DEFAULT_BASE_URL


class OllamaTextClient(OpenResponsesTextClient):
    """Ollama - OpenResponses with default localhost:11434."""

    _default_base_url: ClassVar[str] = DEFAULT_BASE_URL


OllamaTextStream = OpenResponsesTextStream

__all__ = ["OllamaTextClient", "OllamaTextStream"]
