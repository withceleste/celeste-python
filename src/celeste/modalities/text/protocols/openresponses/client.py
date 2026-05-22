"""OpenResponses text client."""

import json
from typing import Any

from celeste.artifacts import DocumentArtifact
from celeste.messages import (
    content_to_text,
    message_parts,
    request_messages,
    require_part,
)
from celeste.parameters import ParameterMapper
from celeste.protocols.openresponses.client import (
    OpenResponsesClient as OpenResponsesMixin,
)
from celeste.protocols.openresponses.streaming import (
    OpenResponsesStream as _OpenResponsesStream,
)
from celeste.protocols.openresponses.tools import (
    parse_content,
    parse_reasoning,
    parse_tool_calls,
)
from celeste.tools import ToolCall, ToolResult
from celeste.types import DocumentPart, ImagePart, Message, Role, TextContent, TextPart
from celeste.utils import build_document_data_url, build_image_data_url

from ...client import TextClient
from ...io import (
    TextChunk,
    TextInput,
)
from ...streaming import TextStream
from .parameters import OPENRESPONSES_PARAMETER_MAPPERS


def _input_file(document: DocumentArtifact) -> dict[str, Any]:
    if document.url and not document.data and not document.path:
        return {"type": "input_file", "file_url": document.url}
    return {
        "type": "input_file",
        "filename": document.path.rsplit("/", 1)[-1] if document.path else "document",
        "file_data": build_document_data_url(document),
    }


def _serialize_content(content: Any) -> Any:
    if isinstance(content, str):
        return content
    items: list[dict[str, Any]] = []
    for part in message_parts(content):
        require_part(
            "OpenResponses",
            part,
            (TextPart, ImagePart, DocumentPart),
        )
        if isinstance(part, TextPart):
            items.append({"type": "input_text", "text": part.text})
        elif isinstance(part, ImagePart):
            items.append(
                {"type": "input_image", "image_url": build_image_data_url(part.image)}
            )
        elif isinstance(part, DocumentPart):
            items.append(_input_file(part.document))
    return items


def _serialize_messages(
    messages: list[Message | ToolResult],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for msg in messages:
        if isinstance(msg, ToolResult):
            items.append(
                {
                    "type": "function_call_output",
                    "call_id": msg.tool_call_id,
                    "output": content_to_text(msg.content),
                }
            )
        elif msg.role == Role.ASSISTANT and (msg.tool_calls or msg.signature):
            sig_blocks = msg.signature
            if sig_blocks:
                items.extend(sig_blocks)
            if msg.content:
                items.append(
                    {
                        "role": msg.role,
                        "content": _serialize_content(msg.content),
                    }
                )
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    items.append(
                        {
                            "type": "function_call",
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments),
                            "call_id": tc.id,
                        }
                    )
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


class OpenResponsesTextStream(_OpenResponsesStream, TextStream):
    """OpenResponses streaming for text modality."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._response_data: dict[str, Any] | None = None

    def _parse_chunk(self, event_data: dict[str, Any]) -> TextChunk | None:
        """Parse one SSE event into a typed chunk (captures response.completed)."""
        event_type = event_data.get("type")
        if event_type == "response.completed":
            response = event_data.get("response")
            if isinstance(response, dict):
                self._response_data = response
        return super()._parse_chunk(event_data)

    def _aggregate_event_data(self, chunks: list[TextChunk]) -> list[dict[str, Any]]:
        """Prepend response_data, then delegate to base."""
        events: list[dict[str, Any]] = []
        if self._response_data is not None:
            events.append(self._response_data)
        events.extend(super()._aggregate_event_data(chunks))
        return events

    def _aggregate_tool_calls(
        self, chunks: list[TextChunk], raw_events: list[dict[str, Any]]
    ) -> list[ToolCall]:
        """Extract tool calls from response.completed data."""
        if self._response_data is None:
            return []
        return parse_tool_calls(self._response_data)

    def _aggregate_signature(
        self, chunks: list[TextChunk], raw_events: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Extract reasoning items from response.completed data."""
        if self._response_data is None:
            return []
        _, signature_blocks = parse_reasoning(self._response_data.get("output", []))
        return signature_blocks


class OpenResponsesTextClient(OpenResponsesMixin, TextClient):
    """OpenResponses text client using Responses API."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return OPENRESPONSES_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """Initialize request with input content."""
        messages = request_messages(
            prompt=inputs.prompt,
            messages=inputs.messages,
            image=inputs.image,
            video=inputs.video,
            audio=inputs.audio,
            document=inputs.document,
        )
        return {"input": _serialize_messages(messages)}

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> TextContent:
        """Parse text content from response."""
        output = super()._parse_content(response_data)
        return parse_content(output)

    def _parse_reasoning(
        self, response_data: dict[str, Any]
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """Parse reasoning from Responses API output."""
        output = response_data.get("output", [])
        return parse_reasoning(output)

    def _parse_tool_calls(self, response_data: dict[str, Any]) -> list[ToolCall]:
        """Parse tool calls from OpenResponses response."""
        return parse_tool_calls(response_data)

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return OpenResponsesTextStream


__all__ = ["OpenResponsesTextClient", "OpenResponsesTextStream"]
