"""Anthropic text client (modality)."""

import base64
from typing import Any, Unpack

from celeste.artifacts import ImageArtifact
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.anthropic.messages.client import AnthropicMessagesClient
from celeste.providers.anthropic.messages.streaming import (
    AnthropicMessagesStream as _AnthropicMessagesStream,
)
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

    def _parse_chunk(self, event_data: dict[str, Any]) -> TextChunk | None:
        """Parse one SSE event into a typed chunk (captures message_start)."""
        event_type = event_data.get("type")
        if event_type == "message_start":
            message = event_data.get("message")
            if isinstance(message, dict):
                self._message_start = message
            return None
        return super()._parse_chunk(event_data)

    def _aggregate_event_data(self, chunks: list[TextChunk]) -> list[dict[str, Any]]:
        """Prepend message_start, then delegate to base."""
        events: list[dict[str, Any]] = []
        if self._message_start is not None:
            events.append({"type": "message_start", "message": self._message_start})
        events.extend(super()._aggregate_event_data(chunks))
        return events


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

                messages.append({"role": role, "content": content})

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

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return AnthropicTextStream


__all__ = ["AnthropicTextClient", "AnthropicTextStream"]
