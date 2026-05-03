"""Anthropic text client (modality)."""

import base64
import contextlib
import json
from typing import Any

from pydantic import BaseModel

from celeste.artifacts import DocumentArtifact, ImageArtifact
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.anthropic.messages.client import AnthropicMessagesClient
from celeste.providers.anthropic.messages.streaming import (
    AnthropicMessagesStream as _AnthropicMessagesStream,
)
from celeste.tools import ToolCall, ToolResult
from celeste.types import TextContent
from celeste.utils import detect_mime_type

from ...client import TextClient
from ...io import (
    TextChunk,
    TextInput,
)
from ...streaming import TextStream
from .parameters import ANTHROPIC_PARAMETER_MAPPERS


class AnthropicTextStream(_AnthropicMessagesStream, TextStream):
    """Anthropic streaming for text modality."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._message_start: dict[str, Any] | None = None
        self._tool_calls: dict[int, dict[str, Any]] = {}
        self._thinking_blocks: list[dict[str, Any]] = []
        self._current_thinking: dict[str, Any] | None = None

    def _parse_chunk(self, event_data: dict[str, Any]) -> TextChunk | None:
        """Parse one SSE event into a typed chunk (captures message_start, tool_use, thinking)."""
        event_type = event_data.get("type")
        if event_type == "message_start":
            message = event_data.get("message")
            if isinstance(message, dict):
                self._message_start = message
            return None
        if event_type == "content_block_start":
            block = event_data.get("content_block", {})
            block_type = block.get("type")
            if block_type == "tool_use":
                idx = event_data.get("index", len(self._tool_calls))
                self._tool_calls[idx] = {
                    "id": block.get("id", ""),
                    "name": block.get("name", ""),
                    "input_json": "",
                }
            elif block_type == "thinking":
                self._current_thinking = {
                    "type": "thinking",
                    "thinking": "",
                    "signature": "",
                }
            elif block_type == "redacted_thinking":
                self._thinking_blocks.append(block)
        elif event_type == "content_block_delta":
            delta = event_data.get("delta", {})
            delta_type = delta.get("type")
            if delta_type == "input_json_delta":
                idx = event_data.get("index", -1)
                if idx in self._tool_calls:
                    self._tool_calls[idx]["input_json"] += delta.get("partial_json", "")
            elif delta_type == "thinking_delta" and self._current_thinking is not None:
                self._current_thinking["thinking"] += delta.get("thinking", "")
            elif delta_type == "signature_delta" and self._current_thinking is not None:
                self._current_thinking["signature"] += delta.get("signature", "")
        elif event_type == "content_block_stop":
            if self._current_thinking is not None:
                self._thinking_blocks.append(self._current_thinking)
                self._current_thinking = None
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

    def _aggregate_signature(
        self, chunks: list[TextChunk], raw_events: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Return accumulated thinking blocks for round-trip signature."""
        return self._thinking_blocks


class AnthropicTextClient(AnthropicMessagesClient, TextClient):
    """Anthropic text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return ANTHROPIC_PARAMETER_MAPPERS

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
                    if isinstance(content, BaseModel):
                        content = content.model_dump_json()
                    elif not isinstance(content, str):
                        content = json.dumps(content, default=str)
                    pending_tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": message.tool_call_id,
                            "content": content,
                        }
                    )
                    continue

                # Flush pending tool results as a single user message
                if pending_tool_results:
                    messages.append({"role": "user", "content": pending_tool_results})
                    pending_tool_results = []

                if role == "assistant" and (message.tool_calls or message.signature):
                    content_blocks: list[dict[str, Any]] = []
                    sig_blocks = message.signature
                    if sig_blocks:
                        content_blocks.extend(sig_blocks)
                    if content:
                        content_blocks.append({"type": "text", "text": str(content)})
                    if message.tool_calls:
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

        if inputs.image is None and inputs.document is None:
            prompt_content: str | list[dict[str, Any]] = inputs.prompt or ""
        else:
            prompt_content = []
            if inputs.image is not None:
                images = (
                    inputs.image if isinstance(inputs.image, list) else [inputs.image]
                )
                for img in images:
                    source = self._build_image_source(img)
                    prompt_content.append({"type": "image", "source": source})
            if inputs.document is not None:
                docs = (
                    inputs.document
                    if isinstance(inputs.document, list)
                    else [inputs.document]
                )
                for doc in docs:
                    source = self._build_document_source(doc)
                    prompt_content.append({"type": "document", "source": source})
            prompt_content.append({"type": "text", "text": inputs.prompt or ""})

        return {"messages": [{"role": "user", "content": prompt_content}]}

    def _build_document_source(self, doc: DocumentArtifact) -> dict[str, Any]:
        """Build Anthropic document source dict from DocumentArtifact."""
        if doc.url:
            return {"type": "url", "url": doc.url}

        doc_bytes = doc.get_bytes()
        mime = doc.mime_type or detect_mime_type(doc_bytes)
        mime_str = str(mime) if mime else "application/pdf"

        base64_data = base64.b64encode(doc_bytes).decode("utf-8")
        return {
            "type": "base64",
            "media_type": mime_str,
            "data": base64_data,
        }

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

    def _parse_reasoning(
        self, response_data: dict[str, Any]
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """Parse thinking blocks from Anthropic response."""
        blocks = response_data.get("content", [])
        reasoning_parts: list[str] = []
        signature_blocks: list[dict[str, Any]] = []
        for block in blocks:
            block_type = block.get("type")
            if block_type == "thinking":
                thinking_text = block.get("thinking", "")
                if thinking_text:
                    reasoning_parts.append(thinking_text)
                signature_blocks.append(block)
            elif block_type == "redacted_thinking":
                signature_blocks.append(block)
        text = "\n".join(reasoning_parts) if reasoning_parts else None
        return text, signature_blocks

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
