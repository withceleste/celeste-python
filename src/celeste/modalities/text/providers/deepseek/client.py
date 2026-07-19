"""DeepSeek text client (modality)."""

from typing import Any

from celeste.parameters import ParameterMapper
from celeste.providers.deepseek.chat.client import DeepSeekChatClient
from celeste.providers.deepseek.chat.streaming import (
    DeepSeekChatStream as _DeepSeekChatStream,
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
from .parameters import DEEPSEEK_PARAMETER_MAPPERS


class DeepSeekTextStream(_DeepSeekChatStream, _ChatCompletionsTextStream):
    """DeepSeek streaming for text modality."""


class DeepSeekTextClient(DeepSeekChatClient, ChatCompletionsTextClient):
    """DeepSeek text client."""

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        request = super()._init_request(inputs)
        for source, serialized in zip(
            inputs.messages or [], request["messages"], strict=False
        ):
            if (
                isinstance(source, Message)
                and source.role == Role.ASSISTANT
                and source.reasoning is not None
                and source.tool_calls is not None
            ):
                serialized["reasoning_content"] = source.reasoning
        return request

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return DEEPSEEK_PARAMETER_MAPPERS

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return DeepSeekTextStream


__all__ = ["DeepSeekTextClient", "DeepSeekTextStream"]
