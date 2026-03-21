"""HuggingFace text client (modality)."""

from celeste.parameters import ParameterMapper
from celeste.providers.huggingface.chat.client import HuggingFaceChatClient
from celeste.providers.huggingface.chat.streaming import (
    HuggingFaceChatStream as _HuggingFaceChatStream,
)
from celeste.types import TextContent

from ...protocols.chatcompletions.client import (
    ChatCompletionsTextClient,
)
from ...protocols.chatcompletions.client import (
    ChatCompletionsTextStream as _ChatCompletionsTextStream,
)
from ...streaming import TextStream
from .parameters import HUGGINGFACE_PARAMETER_MAPPERS


class HuggingFaceTextStream(_HuggingFaceChatStream, _ChatCompletionsTextStream):
    """HuggingFace streaming for text modality."""


class HuggingFaceTextClient(HuggingFaceChatClient, ChatCompletionsTextClient):
    """HuggingFace text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return HUGGINGFACE_PARAMETER_MAPPERS

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return HuggingFaceTextStream


__all__ = ["HuggingFaceTextClient", "HuggingFaceTextStream"]
