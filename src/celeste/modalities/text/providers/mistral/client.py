"""Mistral text client (modality)."""

from typing import Any

from celeste.parameters import ParameterMapper
from celeste.providers.mistral.chat.client import MistralChatClient as MistralChatMixin
from celeste.providers.mistral.chat.streaming import (
    MistralChatStream as _MistralChatStream,
)
from celeste.providers.mistral.chat.streaming import (
    _extract_thinking_text,
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
from .parameters import MISTRAL_PARAMETER_MAPPERS


class MistralTextStream(_MistralChatStream, _ChatCompletionsTextStream):
    """Mistral streaming for text modality."""


class MistralTextClient(MistralChatMixin, ChatCompletionsTextClient):
    """Mistral text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return MISTRAL_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """Initialize request, replaying each reasoning turn's ThinkChunk."""
        request = super()._init_request(inputs)
        for source, serialized in zip(
            inputs.messages or [], request["messages"], strict=False
        ):
            if (
                isinstance(source, Message)
                and source.role == Role.ASSISTANT
                and source.reasoning is not None
            ):
                # Reasoning models need their ThinkChunk replayed on later turns.
                content = serialized.get("content") or []
                serialized["content"] = [
                    {
                        "type": "thinking",
                        "thinking": [{"type": "text", "text": source.reasoning}],
                    },
                    *(
                        [{"type": "text", "text": content}]
                        if isinstance(content, str)
                        else content
                    ),
                ]
        return request

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> TextContent:
        """Parse content from response, handling thinking model list content."""
        content = super()._parse_content(response_data)

        # Handle magistral thinking models that return list content
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            content = "".join(text_parts)

        return content

    def _parse_reasoning(
        self, response_data: dict[str, Any]
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """Parse thinking blocks from Mistral Magistral response."""
        choices = response_data.get("choices", [])
        if not choices:
            return None, []
        message = choices[0].get("message", {})
        content = message.get("content")
        if not isinstance(content, list):
            return None, []
        reasoning_parts = _extract_thinking_text(content)
        text = "\n".join(reasoning_parts) if reasoning_parts else None
        return text, []  # Mistral has no signature for round-trip

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return MistralTextStream


__all__ = ["MistralTextClient", "MistralTextStream"]
