"""OpenResponses text client."""

from typing import Any

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
    serialize_messages,
)
from celeste.tools import ToolCall
from celeste.types import TextContent
from celeste.utils import build_document_data_url, build_image_data_url

from ...client import TextClient
from ...io import (
    TextChunk,
    TextInput,
)
from ...streaming import TextStream
from .parameters import OPENRESPONSES_PARAMETER_MAPPERS


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
        if inputs.messages is not None:
            return {"input": serialize_messages(inputs.messages)}

        content: list[dict[str, Any]] = []
        if inputs.image is not None:
            images = inputs.image if isinstance(inputs.image, list) else [inputs.image]
            for img in images:
                content.append(
                    {"type": "input_image", "image_url": build_image_data_url(img)}
                )

        if inputs.document is not None:
            docs = (
                inputs.document
                if isinstance(inputs.document, list)
                else [inputs.document]
            )
            for doc in docs:
                if doc.url and not doc.data and not doc.path:
                    content.append({"type": "input_file", "file_url": doc.url})
                else:
                    content.append(
                        {
                            "type": "input_file",
                            "filename": doc.path.rsplit("/", 1)[-1]
                            if doc.path
                            else "document",
                            "file_data": build_document_data_url(doc),
                        }
                    )

        content.append({"type": "input_text", "text": inputs.prompt or ""})
        return {"input": [{"role": "user", "content": content}]}

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
