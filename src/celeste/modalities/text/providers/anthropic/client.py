"""Anthropic text client (modality)."""

import base64
import contextlib
from typing import Any, Unpack

from celeste.artifacts import ImageArtifact
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.anthropic.messages.client import AnthropicMessagesClient
from celeste.providers.anthropic.messages.streaming import (
    AnthropicMessagesStream as _AnthropicMessagesStream,
)
from celeste.tools import ToolCall, ToolResult
from celeste.types import ImageContent, Message, TextContent, VideoContent
from celeste.utils import detect_mime_type

from ...client import TextClient
from ...io import (
    TextChunk,
    TextInput,
    TextOutput,
)
from ...parameters import TextParameters
from ...streaming import TextStream
from .parameters import ANTHROPIC_PARAMETER_MAPPERS


class AnthropicTextStream(_AnthropicMessagesStream, TextStream):
    """Anthropic streaming for text modality."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._message_start: dict[str, Any] | None = None
        self._tool_calls: dict[int, dict[str, Any]] = {}

    def _parse_chunk(self, event_data: dict[str, Any]) -> TextChunk | None:
        """Parse one SSE event into a typed chunk (captures message_start and tool_use)."""
        event_type = event_data.get("type")
        if event_type == "message_start":
            message = event_data.get("message")
            if isinstance(message, dict):
                self._message_start = message
            return None
        if event_type == "content_block_start":
            block = event_data.get("content_block", {})
            if block.get("type") == "tool_use":
                idx = event_data.get("index", len(self._tool_calls))
                self._tool_calls[idx] = {
                    "id": block.get("id", ""),
                    "name": block.get("name", ""),
                    "input_json": "",
                }
        elif event_type == "content_block_delta":
            delta = event_data.get("delta", {})
            if delta.get("type") == "input_json_delta":
                idx = event_data.get("index", -1)
                if idx in self._tool_calls:
                    self._tool_calls[idx]["input_json"] += delta.get("partial_json", "")
        return super()._parse_chunk(event_data)

    def _aggregate_event_data(self, chunks: list[TextChunk]) -> list[dict[str, Any]]:
        """Prepend message_start, then delegate to base."""
        events: list[dict[str, Any]] = []
        if self._message_start is not None:
            events.append({"type": "message_start", "message": self._message_start})
        events.extend(super()._aggregate_event_data(chunks))
        return events

    def _aggregate_tool_calls(
        self, chunks: list[TextChunk], raw_events: list[dict[str, Any]]
    ) -> list[ToolCall]:
        """Reconstruct tool calls from accumulated content_block events."""
        import json as _json

        result: list[ToolCall] = []
        for tc in self._tool_calls.values():
            arguments = {}
            if tc["input_json"]:
                with contextlib.suppress(ValueError, TypeError):
                    arguments = _json.loads(tc["input_json"])
            result.append(ToolCall(id=tc["id"], name=tc["name"], arguments=arguments))
        return result


class AnthropicTextClient(AnthropicMessagesClient, TextClient):
    """Anthropic text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return ANTHROPIC_PARAMETER_MAPPERS

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
        prompt: str,
        *,
        messages: list[Message] | None = None,
        image: ImageContent | None = None,
        video: VideoContent | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Analyze image(s) or video(s) with prompt."""
        inputs = TextInput(prompt=prompt, messages=messages, image=image, video=video)
        return await self._predict(inputs, **parameters)

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """Initialize request from Anthropic Messages API format."""
        if inputs.messages is not None:
            system_blocks: list[dict[str, Any]] = []
            messages: list[dict[str, Any]] = []
            pending_tool_results: list[dict[str, Any]] = []

            for message in inputs.messages:
                role = message.role
                content = message.content

                if role in {"system", "developer"}:
                    if isinstance(content, list):
                        for block in content:
                            if isinstance(block, dict):
                                system_blocks.append(block)
                            else:
                                system_blocks.append(
                                    {"type": "text", "text": str(block)}
                                )
                    elif isinstance(content, dict):
                        system_blocks.append(content)
                    elif content is not None:
                        system_blocks.append({"type": "text", "text": str(content)})
                    continue

                if isinstance(message, ToolResult):
                    pending_tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": message.tool_call_id,
                            "content": str(content),
                        }
                    )
                    continue

                # Flush pending tool results as a single user message
                if pending_tool_results:
                    messages.append({"role": "user", "content": pending_tool_results})
                    pending_tool_results = []

                if role == "assistant" and message.tool_calls:
                    content_blocks: list[dict[str, Any]] = []
                    if content:
                        content_blocks.append({"type": "text", "text": str(content)})
                    for tc in message.tool_calls:
                        content_blocks.append(
                            {
                                "type": "tool_use",
                                "id": tc.id,
                                "name": tc.name,
                                "input": tc.arguments,
                            }
                        )
                    messages.append({"role": "assistant", "content": content_blocks})
                else:
                    messages.append({"role": role, "content": content})

            # Flush remaining tool results
            if pending_tool_results:
                messages.append({"role": "user", "content": pending_tool_results})

            request: dict[str, Any] = {"messages": messages}
            if system_blocks:
                request["system"] = system_blocks
            return request

        if inputs.image is None:
            prompt_content: str | list[dict[str, Any]] = inputs.prompt or ""
        else:
            images = inputs.image if isinstance(inputs.image, list) else [inputs.image]
            prompt_content = []
            for img in images:
                source = self._build_image_source(img)
                prompt_content.append({"type": "image", "source": source})
            prompt_content.append({"type": "text", "text": inputs.prompt or ""})

        return {"messages": [{"role": "user", "content": prompt_content}]}

    def _build_image_source(self, img: ImageArtifact) -> dict[str, Any]:
        """Build Anthropic image source dict from ImageArtifact."""
        # Data URL: parse into media_type + base64 data
        if img.url and img.url.startswith("data:") and "," in img.url:
            header, data = img.url.split(",", 1)
            media_type = (
                header.removeprefix("data:").split(";", 1)[0] or ImageMimeType.JPEG
            )
            return {"type": "base64", "media_type": str(media_type), "data": data}

        # Regular URL: pass through
        if img.url:
            return {"type": "url", "url": img.url}

        # Bytes or file path: encode to base64
        image_bytes = img.get_bytes()
        mime = img.mime_type or detect_mime_type(image_bytes)
        mime_str = str(mime) if mime else None

        base64_data = base64.b64encode(image_bytes).decode("utf-8")
        return {
            "type": "base64",
            "media_type": mime_str,
            "data": base64_data,
        }

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> TextContent:
        """Parse content from response."""
        content = super()._parse_content(response_data)

        text_content = ""
        for content_block in content:
            if content_block.get("type") == "text":
                text_content = content_block.get("text") or ""
                break

        return text_content

    def _parse_tool_calls(self, response_data: dict[str, Any]) -> list[ToolCall]:
        """Parse tool calls from Anthropic response."""
        return [
            ToolCall(
                id=block["id"], name=block["name"], arguments=block.get("input", {})
            )
            for block in response_data.get("content", [])
            if block.get("type") == "tool_use"
        ]

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return AnthropicTextStream


__all__ = ["AnthropicTextClient", "AnthropicTextStream"]
