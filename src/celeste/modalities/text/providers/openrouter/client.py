"""OpenRouter text client (OpenResponses protocol)."""

from typing import ClassVar

from celeste.modalities.text.protocols.openresponses.client import (
    OpenResponsesTextClient,
    OpenResponsesTextStream,
)
from celeste.providers.openrouter.config import DEFAULT_BASE_URL


class OpenRouterTextClient(OpenResponsesTextClient):
    """OpenRouter — OpenResponses with default https://openrouter.ai/api."""

    _default_base_url: ClassVar[str] = DEFAULT_BASE_URL


OpenRouterTextStream = OpenResponsesTextStream

__all__ = ["OpenRouterTextClient", "OpenRouterTextStream"]
