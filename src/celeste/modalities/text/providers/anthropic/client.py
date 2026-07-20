"""Anthropic text client (modality)."""

import base64
from typing import Any

from celeste.artifacts import DocumentArtifact, ImageArtifact
from celeste.grounding import Grounding
from celeste.messages import (
    content_to_text,
    message_parts,
    request_messages,
    require_part,
)
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.anthropic.messages.client import (
    AnthropicMessagesClient as AnthropicMessagesMixin,
)
from celeste.providers.anthropic.messages.client import needs_native_replay
from celeste.providers.anthropic.messages.streaming import (
    AnthropicMessagesStream as _AnthropicMessagesStream,
)
from celeste.tools import ToolCall, ToolResult
from celeste.types import DocumentPart, ImagePart, Role, TextContent, TextPart
from celeste.utils import detect_mime_type

from ...client import TextClient
from ...io import (
    TextChunk,
    TextInput,
    TextUsage,
)
from ...streaming import TextStream
from .grounding import parse_grounding
from .parameters import ANTHROPIC_PARAMETER_MAPPERS


class AnthropicTextStream(_AnthropicMessagesStream, TextStream):
    """Anthropic streaming for text modality."""

    def _aggregate_tool_calls(
        self, chunks: list[TextChunk], raw_events: list[dict[str, Any]]
    ) -> list[ToolCall]:
        """Reconstruct tool calls from accumulated content_block events."""
        return [
            ToolCall(
                id=block["id"],
                name=block["name"],
                arguments=block.get("input", {}),
            )
            for block in self._aggregate_content_blocks()
            if block.get("type") == "tool_use"
        ]

    def _aggregate_signature(
        self, chunks: list[TextChunk], raw_events: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Return native content when Anthropic requires exact assistant replay."""
        blocks = self._aggregate_content_blocks()
        return blocks if needs_native_replay(blocks) else []

    def _aggregate_container(
        self, chunks: list[TextChunk], raw_events: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Recover the top-level container from message_start / message_delta events."""
        for event in reversed(raw_events):
            for holder in (event, event.get("message"), event.get("delta")):
                if isinstance(holder, dict) and isinstance(
                    holder.get("container"), dict
                ):
                    return holder["container"]
        return None

    def _usage_from_raw_response(self, raw_response: dict[str, Any]) -> TextUsage:
        """Derive typed usage from the assembled response (usage is split across events)."""
        return self._usage_class(
            **AnthropicMessagesMixin.map_usage_fields(raw_response.get("usage") or {})
        )

    def _aggregate_grounding(
        self, chunks: list[TextChunk], raw_events: list[dict[str, Any]]
    ) -> Grounding | None:
        """Reconstruct Anthropic web-search grounding from streamed content blocks."""
        return parse_grounding(self._aggregate_content_blocks())


class AnthropicTextClient(AnthropicMessagesMixin, TextClient):
    """Anthropic text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return ANTHROPIC_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """Initialize request from Anthropic Messages API format."""

        def content_to_blocks(content: Any) -> list[dict[str, Any]]:
            blocks: list[dict[str, Any]] = []
            for part in message_parts(content):
                require_part(
                    "Anthropic",
                    part,
                    (TextPart, ImagePart, DocumentPart),
                )
                if isinstance(part, TextPart):
                    blocks.append({"type": "text", "text": part.text})
                elif isinstance(part, ImagePart):
                    blocks.append(
                        {
                            "type": "image",
                            "source": self._build_image_source(part.image),
                        }
                    )
                elif isinstance(part, DocumentPart):
                    blocks.append(
                        {
                            "type": "document",
                            "source": self._build_document_source(part.document),
                        }
                    )
            return blocks

        system_blocks: list[dict[str, Any]] = []
        messages: list[dict[str, Any]] = []
        pending_tool_results: list[dict[str, Any]] = []
        container_id: str | None = None

        for message in request_messages(
            prompt=inputs.prompt,
            messages=inputs.messages,
            image=inputs.image,
            video=inputs.video,
            audio=inputs.audio,
            document=inputs.document,
        ):
            role = message.role
            content = message.content

            if role in {Role.SYSTEM, Role.DEVELOPER}:
                system_blocks.extend(content_to_blocks(content))
                continue

            if isinstance(message, ToolResult):
                pending_tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": message.tool_call_id,
                        "content": content_to_text(message.content),
                    }
                )
                continue

            # Flush pending tool results as a single user message
            if pending_tool_results:
                messages.append({"role": "user", "content": pending_tool_results})
                pending_tool_results = []

            # Last-wins: the pending turn's code-execution container is echoed top-level.
            if message.container and message.container.get("id"):
                container_id = message.container["id"]

            if role == Role.ASSISTANT and (message.tool_calls or message.signature):
                sig_blocks = message.signature or []
                if any(
                    b.get("type") not in {"thinking", "redacted_thinking"}
                    for b in sig_blocks
                ):
                    # thinking signs block positions — echo the full original turn verbatim
                    messages.append({"role": "assistant", "content": sig_blocks})
                    continue
                content_blocks: list[dict[str, Any]] = []
                if sig_blocks:
                    content_blocks.extend(sig_blocks)
                if content:
                    content_blocks.extend(content_to_blocks(content))
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
                messages.append({"role": role, "content": content_to_blocks(content)})

        # Flush remaining tool results
        if pending_tool_results:
            messages.append({"role": "user", "content": pending_tool_results})

        request: dict[str, Any] = {"messages": messages}
        if system_blocks:
            request["system"] = system_blocks
        if container_id:
            request["container"] = container_id
        return request

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
        """Parse thinking from Anthropic response (signature = full content array)."""
        blocks = response_data.get("content", [])
        reasoning_parts = [
            b["thinking"]
            for b in blocks
            if b.get("type") == "thinking" and b.get("thinking")
        ]
        text = "\n".join(reasoning_parts) if reasoning_parts else None
        return text, list(blocks) if needs_native_replay(blocks) else []

    def _parse_tool_calls(self, response_data: dict[str, Any]) -> list[ToolCall]:
        """Parse tool calls from Anthropic response."""
        return [
            ToolCall(
                id=block["id"], name=block["name"], arguments=block.get("input", {})
            )
            for block in response_data.get("content", [])
            if block.get("type") == "tool_use"
        ]

    def _parse_grounding(self, response_data: dict[str, Any]) -> Grounding | None:
        """Parse Anthropic web-search grounding from Messages content blocks."""
        return parse_grounding(super()._parse_content(response_data))

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return AnthropicTextStream


__all__ = ["AnthropicTextClient", "AnthropicTextStream"]
