"""Chat Completions text client."""

import json
from typing import Any

from celeste.grounding import Grounding
from celeste.messages import (
    content_to_text,
    message_parts,
    request_messages,
    require_part,
)
from celeste.parameters import ParameterMapper
from celeste.protocols.chatcompletions.client import (
    ChatCompletionsClient as ChatCompletionsMixin,
)
from celeste.protocols.chatcompletions.streaming import (
    ChatCompletionsStream as _ChatCompletionsStream,
)
from celeste.protocols.chatcompletions.tools import (
    parse_annotations,
    parse_tool_calls,
)
from celeste.tools import ToolCall, ToolResult
from celeste.types import (
    DocumentPart,
    ImagePart,
    Message,
    Role,
    TextContent,
    TextPart,
    VideoPart,
)
from celeste.utils import build_data_url

from ...client import TextClient
from ...grounding import map_url_citation_annotations
from ...io import (
    TextChunk,
    TextInput,
)
from ...streaming import TextStream
from .parameters import CHATCOMPLETIONS_PARAMETER_MAPPERS


def _serialize_content(content: Any) -> Any:
    if isinstance(content, str):
        return content
    items: list[dict[str, Any]] = []
    for part in message_parts(content):
        require_part(
            "Chat Completions",
            part,
            (TextPart, ImagePart, VideoPart, DocumentPart),
        )
        if isinstance(part, TextPart):
            items.append({"type": "text", "text": part.text})
        elif isinstance(part, ImagePart):
            items.append(
                {
                    "type": "image_url",
                    "image_url": {"url": build_data_url(part.image)},
                }
            )
        elif isinstance(part, VideoPart):
            items.append(
                {
                    "type": "video_url",
                    "video_url": {"url": build_data_url(part.video)},
                }
            )
        elif isinstance(part, DocumentPart):
            items.append(
                {
                    "type": "document_url",
                    "document_url": build_data_url(part.document),
                }
            )
    return items


def _serialize_messages(
    messages: list[Message | ToolResult],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for msg in messages:
        if isinstance(msg, ToolResult):
            items.append(
                {
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id,
                    "content": content_to_text(msg.content),
                }
            )
        elif msg.role == Role.ASSISTANT and msg.tool_calls:
            msg_dict = msg.model_dump(
                exclude={"content", "tool_calls", "reasoning", "signature"},
                exclude_none=True,
                mode="json",
                serialize_as_any=True,
            )
            msg_dict["content"] = _serialize_content(msg.content)
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
                exclude={"content", "tool_calls", "reasoning", "signature"},
                exclude_none=True,
                mode="json",
                serialize_as_any=True,
            )
            msg_dict["content"] = _serialize_content(msg.content)
            items.append(msg_dict)
    return items


class ChatCompletionsTextStream(_ChatCompletionsStream, TextStream):
    """Chat Completions streaming for text modality."""

    def _aggregate_grounding(
        self, chunks: list[TextChunk], raw_events: list[dict[str, Any]]
    ) -> Grounding | None:
        """Aggregate URL citations from streamed Chat Completions annotations."""
        return map_url_citation_annotations(self._annotations)


class ChatCompletionsTextClient(ChatCompletionsMixin, TextClient):
    """Chat Completions text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return CHATCOMPLETIONS_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """Initialize request with Chat Completions message format."""
        messages = request_messages(
            prompt=inputs.prompt,
            messages=inputs.messages,
            image=inputs.image,
            video=inputs.video,
            audio=inputs.audio,
            document=inputs.document,
        )
        return {"messages": _serialize_messages(messages)}

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

    def _parse_grounding(self, response_data: dict[str, Any]) -> Grounding | None:
        """Parse grounding from Chat Completions citation/search extensions."""
        return map_url_citation_annotations(parse_annotations(response_data))

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return ChatCompletionsTextStream


__all__ = ["ChatCompletionsTextClient", "ChatCompletionsTextStream"]
