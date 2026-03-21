"""DeepSeek text client (modality)."""

from celeste.parameters import ParameterMapper
from celeste.providers.deepseek.chat.client import DeepSeekChatClient
from celeste.providers.deepseek.chat.streaming import (
    DeepSeekChatStream as _DeepSeekChatStream,
)
from celeste.types import TextContent

from ...protocols.chatcompletions.client import (
    ChatCompletionsTextClient,
)
from ...protocols.chatcompletions.client import (
    ChatCompletionsTextStream as _ChatCompletionsTextStream,
)
from ...streaming import TextStream
from .parameters import DEEPSEEK_PARAMETER_MAPPERS


class DeepSeekTextStream(_DeepSeekChatStream, _ChatCompletionsTextStream):
    """DeepSeek streaming for text modality."""


class DeepSeekTextClient(DeepSeekChatClient, ChatCompletionsTextClient):
    """DeepSeek text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return DEEPSEEK_PARAMETER_MAPPERS

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return DeepSeekTextStream


__all__ = ["DeepSeekTextClient", "DeepSeekTextStream"]
