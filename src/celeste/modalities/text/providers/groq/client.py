"""Groq text client (modality)."""

from typing import Any

from celeste.grounding import Grounding, GroundingSource
from celeste.parameters import ParameterMapper
from celeste.providers.groq.chat.client import GroqChatClient as GroqChatMixin
from celeste.providers.groq.chat.streaming import GroqChatStream as _GroqChatStream
from celeste.providers.groq.chat.tools import parse_search_results
from celeste.types import TextContent

from ...protocols.chatcompletions.client import (
    ChatCompletionsTextClient,
)
from ...protocols.chatcompletions.client import (
    ChatCompletionsTextStream as _ChatCompletionsTextStream,
)
from ...streaming import TextStream
from .parameters import GROQ_PARAMETER_MAPPERS


class GroqTextStream(_GroqChatStream, _ChatCompletionsTextStream):
    """Groq streaming for text modality."""


class GroqTextClient(GroqChatMixin, ChatCompletionsTextClient):
    """Groq text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return GROQ_PARAMETER_MAPPERS

    def _parse_grounding(self, response_data: dict[str, Any]) -> Grounding | None:
        """Parse Groq Compound search results into grounding sources."""
        sources: list[GroundingSource] = []
        seen: set[tuple[str, str | None]] = set()
        for result in parse_search_results(response_data):
            url = result.get("url")
            if not isinstance(url, str):
                continue
            title = result.get("title")
            key = (url, title if isinstance(title, str) else None)
            if key in seen:
                continue
            seen.add(key)
            sources.append(GroundingSource(url=url, title=key[1]))

        return Grounding(sources=sources) if sources else None

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return GroqTextStream


__all__ = ["GroqTextClient", "GroqTextStream"]
