"""Moonshot text client (modality)."""

from celeste.parameters import ParameterMapper
from celeste.providers.moonshot.chat.client import MoonshotChatClient
from celeste.providers.moonshot.chat.streaming import (
    MoonshotChatStream as _MoonshotChatStream,
)
from celeste.types import TextContent

from ...protocols.chatcompletions.client import (
    ChatCompletionsTextClient,
)
from ...protocols.chatcompletions.client import (
    ChatCompletionsTextStream as _ChatCompletionsTextStream,
)
from ...streaming import TextStream
from .parameters import MOONSHOT_PARAMETER_MAPPERS


class MoonshotTextStream(_MoonshotChatStream, _ChatCompletionsTextStream):
    """Moonshot streaming for text modality."""


class MoonshotTextClient(MoonshotChatClient, ChatCompletionsTextClient):
    """Moonshot text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return MOONSHOT_PARAMETER_MAPPERS

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return MoonshotTextStream


__all__ = ["MoonshotTextClient", "MoonshotTextStream"]
