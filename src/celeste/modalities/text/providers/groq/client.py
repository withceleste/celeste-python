"""Groq text client (modality)."""

from typing import Any

from celeste.grounding import Grounding
from celeste.parameters import ParameterMapper
from celeste.providers.groq.chat.client import GroqChatClient as GroqChatMixin
from celeste.providers.groq.chat.streaming import GroqChatStream as _GroqChatStream
from celeste.types import TextContent

from ...io import TextChunk
from ...protocols.chatcompletions.client import (
    ChatCompletionsTextClient,
)
from ...protocols.chatcompletions.client import (
    ChatCompletionsTextStream as _ChatCompletionsTextStream,
)
from ...streaming import TextStream
from .grounding import parse_grounding
from .parameters import GROQ_PARAMETER_MAPPERS


class GroqTextStream(_GroqChatStream, _ChatCompletionsTextStream):
    """Groq streaming for text modality."""

    def _aggregate_grounding(
        self, chunks: list[TextChunk], raw_events: list[dict[str, Any]]
    ) -> Grounding | None:
        """Parse Groq search results from streamed executed_tools deltas."""
        return parse_grounding(self._executed_tools)


class GroqTextClient(GroqChatMixin, ChatCompletionsTextClient):
    """Groq text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return GROQ_PARAMETER_MAPPERS

    def _parse_grounding(self, response_data: dict[str, Any]) -> Grounding | None:
        """Parse Groq search results from the message's executed_tools."""
        choices = response_data.get("choices", [])
        if not choices:
            return None
        return parse_grounding(choices[0].get("message", {}).get("executed_tools"))

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return GroqTextStream


__all__ = ["GroqTextClient", "GroqTextStream"]
