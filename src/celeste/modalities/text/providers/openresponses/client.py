"""OpenResponses text client."""

import json
from typing import Any, Unpack

from celeste.parameters import ParameterMapper
from celeste.protocols.openresponses.client import (
    OpenResponsesClient as OpenResponsesMixin,
)
from celeste.protocols.openresponses.streaming import (
    OpenResponsesStream as _OpenResponsesStream,
)
from celeste.tools import ToolCall, ToolResult
from celeste.types import ImageContent, Message, TextContent, VideoContent
from celeste.utils import build_image_data_url

from ...client import TextClient
from ...io import (
    TextChunk,
    TextInput,
    TextOutput,
)
from ...parameters import TextParameters
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
        return [
            ToolCall(
                id=item.get("call_id", item.get("id", "")),
                name=item["name"],
                arguments=json.loads(item["arguments"])
                if isinstance(item.get("arguments"), str)
                else item.get("arguments", {}),
            )
            for item in self._response_data.get("output", [])
            if item.get("type") == "function_call"
        ]


class OpenResponsesTextClient(OpenResponsesMixin, TextClient):
    """OpenResponses text client using Responses API."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return OPENRESPONSES_PARAMETER_MAPPERS

    async def generate(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Generate text from prompt."""
        inputs = TextInput(prompt=prompt, messages=messages)
        return await self._predict(
            inputs, base_url=base_url, extra_body=extra_body, **parameters
        )

    async def analyze(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        image: ImageContent | None = None,
        video: VideoContent | None = None,
        base_url: str | None = None,
        extra_body: dict[str, Any] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Analyze image(s) or video(s) with prompt or messages."""
        inputs = TextInput(prompt=prompt, messages=messages, image=image, video=video)
        return await self._predict(
            inputs, base_url=base_url, extra_body=extra_body, **parameters
        )

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """Initialize request with input content."""
        if inputs.messages is not None:
            items: list[dict[str, Any]] = []
            for msg in inputs.messages:
                if isinstance(msg, ToolResult):
                    items.append(
                        {
                            "type": "function_call_output",
                            "call_id": msg.tool_call_id,
                            "output": str(msg.content),
                        }
                    )
                else:
                    items.append(msg.model_dump())
            return {"input": items}

        content: list[dict[str, Any]] = []
        if inputs.image is not None:
            images = inputs.image if isinstance(inputs.image, list) else [inputs.image]
            for img in images:
                content.append(
                    {"type": "input_image", "image_url": build_image_data_url(img)}
                )

        content.append({"type": "input_text", "text": inputs.prompt or ""})
        return {"input": [{"role": "user", "content": content}]}

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> TextContent:
        """Parse text content from response."""
        output = super()._parse_content(response_data)
        for item in output:
            if item.get("type") == "message":
                for part in item.get("content", []):
                    if part.get("type") == "output_text":
                        text = part.get("text") or ""
                        return text

        return ""

    def _parse_tool_calls(self, response_data: dict[str, Any]) -> list[ToolCall]:
        """Parse tool calls from OpenResponses response."""
        return [
            ToolCall(
                id=item.get("call_id", item.get("id", "")),
                name=item["name"],
                arguments=json.loads(item["arguments"])
                if isinstance(item.get("arguments"), str)
                else item.get("arguments", {}),
            )
            for item in response_data.get("output", [])
            if item.get("type") == "function_call"
        ]

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return OpenResponsesTextStream


__all__ = ["OpenResponsesTextClient", "OpenResponsesTextStream"]
