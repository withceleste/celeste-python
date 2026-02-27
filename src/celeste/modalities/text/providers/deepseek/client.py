"""DeepSeek text client (modality)."""

from typing import Any, Unpack

from celeste.parameters import ParameterMapper
from celeste.providers.deepseek.chat.client import DeepSeekChatClient
from celeste.providers.deepseek.chat.streaming import (
    DeepSeekChatStream as _DeepSeekChatStream,
)
from celeste.types import Message, TextContent

from ...client import TextClient
from ...io import (
    TextInput,
    TextOutput,
)
from ...parameters import TextParameters
from ...streaming import TextStream
from .parameters import DEEPSEEK_PARAMETER_MAPPERS


class DeepSeekTextStream(_DeepSeekChatStream, TextStream):
    """DeepSeek streaming for text modality."""


class DeepSeekTextClient(DeepSeekChatClient, TextClient):
    """DeepSeek text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return DEEPSEEK_PARAMETER_MAPPERS

    async def generate(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Generate text from prompt."""
        inputs = TextInput(prompt=prompt, messages=messages)
        return await self._predict(inputs, **parameters)

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """Initialize request from DeepSeek messages array format."""
        # If messages provided, use them directly (messages take precedence)
        if inputs.messages is not None:
            return {"messages": [message.model_dump() for message in inputs.messages]}

        # Fall back to prompt-based input
        messages = [
            {
                "role": "user",
                "content": inputs.prompt or "",
            }
        ]

        return {"messages": messages}

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> TextContent:
        """Parse content from response."""
        choices = super()._parse_content(response_data)
        message = choices[0].get("message", {})
        content = message.get("content") or ""
        return content

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return DeepSeekTextStream


__all__ = ["DeepSeekTextClient", "DeepSeekTextStream"]
