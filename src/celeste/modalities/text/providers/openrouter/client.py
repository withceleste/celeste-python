"""OpenRouter text client (OpenResponses protocol)."""

from typing import Any, ClassVar

from celeste.modalities.text.io import TextChunk
from celeste.modalities.text.protocols.openresponses.client import (
    OpenResponsesTextClient,
    OpenResponsesTextStream,
)
from celeste.modalities.text.streaming import TextStream
from celeste.protocols.openresponses.tools import native_replay_output
from celeste.providers.openrouter.config import DEFAULT_BASE_URL


class OpenRouterTextStream(OpenResponsesTextStream):
    """OpenRouter streaming for text modality."""

    def _aggregate_signature(
        self, chunks: list[TextChunk], raw_events: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Return every output item when stateless replay must resend them in order."""
        if self._response_data is None:
            return []
        return native_replay_output(self._response_data.get("output", []))


class OpenRouterTextClient(OpenResponsesTextClient):
    """OpenRouter — OpenResponses with default https://openrouter.ai/api."""

    _default_base_url: ClassVar[str] = DEFAULT_BASE_URL

    def _parse_reasoning(
        self, response_data: dict[str, Any]
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """Parse reasoning; keep every output item when replay must resend them in order."""
        text, _ = super()._parse_reasoning(response_data)
        return text, native_replay_output(response_data.get("output", []))

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return OpenRouterTextStream


__all__ = ["OpenRouterTextClient", "OpenRouterTextStream"]
