"""OpenRouter text client (OpenResponses protocol)."""

import os
from typing import ClassVar

from celeste.modalities.text.protocols.openresponses.client import (
    OpenResponsesTextClient,
    OpenResponsesTextStream,
)
from celeste.providers.openrouter.config import DEFAULT_BASE_URL


class OpenRouterTextClient(OpenResponsesTextClient):
    """OpenRouter — OpenResponses with default https://openrouter.ai/api."""

    _default_base_url: ClassVar[str] = DEFAULT_BASE_URL

    def _json_headers(
        self, extra_headers: dict[str, str] | None = None
    ) -> dict[str, str]:
        headers = super()._json_headers(extra_headers)
        referer = os.environ.get("OPENROUTER_HTTP_REFERER")
        if referer:
            headers["HTTP-Referer"] = referer
        title = os.environ.get("OPENROUTER_APP_TITLE")
        if title:
            headers["X-OpenRouter-Title"] = title
        return headers


OpenRouterTextStream = OpenResponsesTextStream

__all__ = ["OpenRouterTextClient", "OpenRouterTextStream"]
