"""Groq text client (modality)."""

from celeste.parameters import ParameterMapper
from celeste.providers.groq.chat.client import GroqChatClient
from celeste.providers.groq.chat.streaming import GroqChatStream as _GroqChatStream
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


class GroqTextClient(GroqChatClient, ChatCompletionsTextClient):
    """Groq text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return GROQ_PARAMETER_MAPPERS

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return GroqTextStream


__all__ = ["GroqTextClient", "GroqTextStream"]
