"""OpenAI text client."""

import json
from typing import Any, Unpack

from celeste.parameters import ParameterMapper
from celeste.providers.openai.responses.client import (
    OpenAIResponsesClient as OpenAIResponsesMixin,
)
from celeste.providers.openai.responses.streaming import (
    OpenAIResponsesStream as _OpenAIResponsesStream,
)
from celeste.tools import ToolCall, ToolResult
from celeste.types import ImageContent, Message, TextContent, VideoContent
from celeste.utils import build_image_data_url

from ...client import TextClient
from ...io import (
    TextInput,
    TextOutput,
)
from ...parameters import TextParameters
from ...streaming import TextStream
from ..openresponses.client import OpenResponsesTextStream
from .parameters import OPENAI_PARAMETER_MAPPERS


class OpenAITextStream(_OpenAIResponsesStream, OpenResponsesTextStream):
    """OpenAI streaming for text modality."""


class OpenAITextClient(OpenAIResponsesMixin, TextClient):
    """OpenAI text client using Responses API."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return OPENAI_PARAMETER_MAPPERS

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

    async def analyze(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        image: ImageContent | None = None,
        video: VideoContent | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Analyze image(s) or video(s) with prompt or messages."""
        inputs = TextInput(prompt=prompt, messages=messages, image=image, video=video)
        return await self._predict(inputs, **parameters)

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
        **parameters: Unpack[TextParameters],
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
        """Parse tool calls from OpenAI response."""
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
        return OpenAITextStream


__all__ = ["OpenAITextClient", "OpenAITextStream"]
