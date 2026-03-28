"""Chat Completions text client."""

from typing import Any

from celeste.parameters import ParameterMapper
from celeste.protocols.chatcompletions.client import (
    ChatCompletionsClient as ChatCompletionsMixin,
)
from celeste.protocols.chatcompletions.streaming import (
    ChatCompletionsStream as _ChatCompletionsStream,
)
from celeste.protocols.chatcompletions.tools import (
    parse_tool_calls,
    serialize_messages,
)
from celeste.tools import ToolCall
from celeste.types import TextContent
from celeste.utils import build_document_data_url, build_image_data_url

from ...client import TextClient
from ...io import (
    TextInput,
)
from ...streaming import TextStream
from .parameters import CHATCOMPLETIONS_PARAMETER_MAPPERS


class ChatCompletionsTextStream(_ChatCompletionsStream, TextStream):
    """Chat Completions streaming for text modality."""


class ChatCompletionsTextClient(ChatCompletionsMixin, TextClient):
    """Chat Completions text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return CHATCOMPLETIONS_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """Initialize request with Chat Completions message format."""
        if inputs.messages is not None:
            return {"messages": serialize_messages(inputs.messages)}

        if inputs.image is None and inputs.document is None:
            content: str | list[dict[str, Any]] = inputs.prompt or ""
        else:
            content = []
            if inputs.image is not None:
                images = (
                    inputs.image if isinstance(inputs.image, list) else [inputs.image]
                )
                for img in images:
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": build_image_data_url(img)},
                        }
                    )
            if inputs.document is not None:
                docs = (
                    inputs.document
                    if isinstance(inputs.document, list)
                    else [inputs.document]
                )
                for doc in docs:
                    content.append(
                        {
                            "type": "document_url",
                            "document_url": build_document_data_url(doc),
                        }
                    )
            content.append({"type": "text", "text": inputs.prompt or ""})

        return {"messages": [{"role": "user", "content": content}]}

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> TextContent:
        """Parse text content from response."""
        choices = super()._parse_content(response_data)
        message = choices[0].get("message", {})
        content = message.get("content") or ""
        return content

    def _parse_tool_calls(self, response_data: dict[str, Any]) -> list[ToolCall]:
        """Parse tool calls from Chat Completions response."""
        return parse_tool_calls(response_data)

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return ChatCompletionsTextStream


__all__ = ["ChatCompletionsTextClient", "ChatCompletionsTextStream"]
