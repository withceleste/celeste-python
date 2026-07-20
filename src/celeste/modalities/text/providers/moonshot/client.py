"""Moonshot text client (modality)."""

from typing import Any

from celeste.parameters import ParameterMapper
from celeste.providers.moonshot.chat.client import (
    MoonshotChatClient as MoonshotChatMixin,
)
from celeste.providers.moonshot.chat.streaming import (
    MoonshotChatStream as _MoonshotChatStream,
)
from celeste.types import Message, Role, TextContent

from ...io import TextInput
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


class MoonshotTextClient(MoonshotChatMixin, ChatCompletionsTextClient):
    """Moonshot text client."""

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        request = super()._init_request(inputs)
        for source, serialized in zip(
            inputs.messages or [], request["messages"], strict=False
        ):
            if (
                isinstance(source, Message)
                and source.role == Role.ASSISTANT
                and source.reasoning is not None
            ):
                serialized["reasoning_content"] = source.reasoning
        return request

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return MOONSHOT_PARAMETER_MAPPERS

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return MoonshotTextStream


__all__ = ["MoonshotTextClient", "MoonshotTextStream"]
