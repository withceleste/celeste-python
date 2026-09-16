"""xAI text client (modality)."""

import base64
from typing import Any

from asgiref.sync import async_to_sync
from pydantic import BaseModel

from celeste.artifacts import ImageArtifact
from celeste.messages import request_messages
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.xai.responses.client import (
    XAIResponsesClient as XAIResponsesMixin,
)
from celeste.providers.xai.responses.config import XAIResponsesEndpoint
from celeste.providers.xai.responses.streaming import (
    XAIResponsesStream as _XAIResponsesStream,
)
from celeste.tools import ToolResult
from celeste.types import ImagePart, Message, Role, TextContent, TextPart
from celeste.utils import detect_mime_type

from ...client import TextSyncNamespace
from ...io import TextChunk, TextInput
from ...protocols.openresponses.client import (
    OpenResponsesTextClient,
    _serialize_messages,
)
from ...protocols.openresponses.client import (
    OpenResponsesTextStream as _OpenResponsesTextStream,
)
from ...streaming import TextStream
from .io import XAITextOutput
from .parameters import XAI_PARAMETER_MAPPERS


def _has_image_output(output: list[dict[str, Any]]) -> bool:
    """Identify native image output items."""
    return any(item.get("type") == "image_generation_call" for item in output)


def _has_native_output(output: list[dict[str, Any]]) -> bool:
    """Identify output that must be replayed as a complete native sequence."""
    return any(
        item.get("type") in ("image_generation_call", "compaction") for item in output
    )


def _parse_image_content(output: list[dict[str, Any]]) -> list[BaseModel]:
    """Decode images and text in their original output order."""
    parts: list[BaseModel] = []
    for item in output:
        if item.get("type") == "message":
            parts.extend(
                TextPart(text=part.get("text") or "")
                for part in item.get("content", [])
                if part.get("type") == "output_text"
            )
        elif item.get("type") == "image_generation_call":
            result = item.get("result")
            if not isinstance(result, str) or not result:
                msg = "image_generation_call result must be a base64 string"
                raise ValueError(msg)
            data = base64.b64decode(result, validate=True)
            mime = detect_mime_type(data)
            parts.append(
                ImagePart(
                    image=ImageArtifact(
                        data=data,
                        mime_type=mime if isinstance(mime, ImageMimeType) else None,
                        metadata={k: v for k, v in item.items() if k != "result"},
                    )
                )
            )
    return parts


class XAITextStream(_XAIResponsesStream, _OpenResponsesTextStream):
    """xAI streaming for text modality."""

    _output_class = XAITextOutput

    def _aggregate_content(self, chunks: list[TextChunk]) -> TextContent:
        """Include completed native images in the final output."""
        if self._response_data is not None:
            output = self._response_data.get("output", [])
            if _has_image_output(output):
                return _parse_image_content(output)
        return super()._aggregate_content(chunks)

    def _aggregate_signature(
        self, chunks: list[TextChunk], raw_events: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Preserve the complete native sequence for continuation."""
        if self._response_data is not None:
            output = self._response_data.get("output", [])
            if _has_native_output(output):
                return list(output)
        return super()._aggregate_signature(chunks, raw_events)


class XAITextClient(XAIResponsesMixin, OpenResponsesTextClient):
    """xAI text client."""

    @classmethod
    def _output_class(cls) -> type[XAITextOutput]:
        """Return the output type that preserves native images."""
        return XAITextOutput

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return XAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """xAI accepts plain string input for text-only requests."""
        has_media = any(
            media is not None
            for media in (inputs.image, inputs.video, inputs.audio, inputs.document)
        )
        if inputs.messages is None and not has_media:
            return {"input": inputs.prompt or ""}
        items: list[dict[str, Any]] = []
        for message in request_messages(
            prompt=inputs.prompt,
            messages=inputs.messages,
            image=inputs.image,
            video=inputs.video,
            audio=inputs.audio,
            document=inputs.document,
        ):
            if (
                isinstance(message, Message)
                and message.role == Role.ASSISTANT
                and message.signature
                and _has_native_output(message.signature)
            ):
                items.extend(message.signature)
            else:
                items.extend(_serialize_messages([message]))
        return {"input": items}

    def _parse_content(self, response_data: dict[str, Any]) -> TextContent:
        """Include native image results alongside text."""
        output = response_data.get("output", [])
        if _has_image_output(output):
            return _parse_image_content(output)
        return super()._parse_content(response_data)

    def _parse_reasoning(
        self, response_data: dict[str, Any]
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """Preserve opaque compaction and image output for verbatim replay."""
        reasoning, signature = super()._parse_reasoning(response_data)
        output = response_data.get("output", [])
        return reasoning, list(output) if _has_native_output(output) else signature

    async def compact(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message | ToolResult] | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> XAITextOutput:
        """Compact conversation context into opaque replayable output."""
        self._check_media_support(messages=messages)
        return await self._predict(
            TextInput(prompt=prompt, messages=messages),
            endpoint=XAIResponsesEndpoint.COMPACT_RESPONSE,
            extra_body=extra_body,
            extra_headers=extra_headers,
        )

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return XAITextStream

    @property
    def sync(self) -> "XAITextSyncNamespace":
        """Synchronous xAI text operations."""
        return XAITextSyncNamespace(self)


class XAITextSyncNamespace(TextSyncNamespace):
    """Synchronous xAI text operations."""

    def __init__(self, client: XAITextClient) -> None:
        self._client = client

    def compact(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message | ToolResult] | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> XAITextOutput:
        """Blocking context compaction."""
        return async_to_sync(self._client.compact)(
            prompt,
            messages=messages,
            extra_body=extra_body,
            extra_headers=extra_headers,
        )


__all__ = ["XAITextClient", "XAITextStream", "XAITextSyncNamespace"]
