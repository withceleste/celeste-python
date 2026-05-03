"""Chat Completions text client."""

import json
from typing import Any

from pydantic import BaseModel

from celeste.parameters import ParameterMapper
from celeste.protocols.chatcompletions.client import (
    ChatCompletionsClient as ChatCompletionsMixin,
)
from celeste.protocols.chatcompletions.streaming import (
    ChatCompletionsStream as _ChatCompletionsStream,
)
from celeste.protocols.chatcompletions.tools import parse_tool_calls
from celeste.tools import ToolCall, ToolResult
from celeste.types import Message, TextContent
from celeste.utils import build_document_data_url, build_image_data_url

from ...client import TextClient
from ...io import (
    TextInput,
)
from ...streaming import TextStream
from .parameters import CHATCOMPLETIONS_PARAMETER_MAPPERS


def _chat_completions_text_messages(
    messages: list[Message],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for msg in messages:
        if isinstance(msg, ToolResult):
            content = msg.content
            if isinstance(content, BaseModel):
                content = content.model_dump_json()
            elif not isinstance(content, str):
                content = json.dumps(content, default=str)
            items.append(
                {
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id,
                    "content": content,
                }
            )
        elif msg.role == "assistant" and msg.tool_calls:
            msg_dict = msg.model_dump(
                exclude_none=True,
                mode="json",
                serialize_as_any=True,
            )
            msg_dict.pop("reasoning", None)
            msg_dict.pop("signature", None)
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.arguments),
                    },
                }
                for tc in msg.tool_calls
            ]
            items.append(msg_dict)
        else:
            msg_dict = msg.model_dump(
                exclude_none=True,
                mode="json",
                serialize_as_any=True,
            )
            msg_dict.pop("tool_calls", None)
            msg_dict.pop("reasoning", None)
            msg_dict.pop("signature", None)
            items.append(msg_dict)
    return items


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
            return {"messages": _chat_completions_text_messages(inputs.messages)}

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

    def _parse_reasoning(
        self, response_data: dict[str, Any]
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """Parse reasoning_content from Chat Completions response."""
        choices = response_data.get("choices", [])
        if not choices:
            return None, []
        reasoning = choices[0].get("message", {}).get("reasoning_content")
        return reasoning, []  # empty signature — must NOT send back

    def _parse_tool_calls(self, response_data: dict[str, Any]) -> list[ToolCall]:
        """Parse tool calls from Chat Completions response."""
        return parse_tool_calls(response_data)

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return ChatCompletionsTextStream


__all__ = ["ChatCompletionsTextClient", "ChatCompletionsTextStream"]
