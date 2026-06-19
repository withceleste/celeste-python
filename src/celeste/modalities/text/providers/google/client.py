"""Google text client (modality)."""

from typing import Any
from uuid import uuid4

from celeste.grounding import Grounding
from celeste.messages import (
    message_parts,
    request_messages,
    tool_result_object,
)
from celeste.parameters import ParameterMapper
from celeste.providers.google.generate_content.client import GoogleGenerateContentClient
from celeste.providers.google.generate_content.grounding import (
    merge_grounding_metadata,
    parse_grounding_metadata,
)
from celeste.providers.google.generate_content.streaming import (
    GoogleGenerateContentStream as _GoogleGenerateContentStream,
)
from celeste.providers.google.utils import build_media_part
from celeste.tools import ToolCall, ToolResult
from celeste.types import (
    AudioPart,
    DocumentPart,
    ImagePart,
    Role,
    TextContent,
    TextPart,
    VideoPart,
)

from ...client import TextClient
from ...io import TextInput
from ...streaming import TextStream
from .grounding import map_grounding
from .parameters import GOOGLE_PARAMETER_MAPPERS


class GoogleTextStream(_GoogleGenerateContentStream, TextStream):
    """Google streaming for text modality."""

    def _aggregate_grounding(
        self, chunks: list, raw_events: list[dict[str, Any]]
    ) -> Grounding | None:
        """Aggregate Google grounding metadata into text grounding."""
        metadata = getattr(self, "_grounding_metadata", None)
        if not metadata:
            return None
        return map_grounding(
            merge_grounding_metadata(metadata),
            self._aggregate_content(chunks),
        )

    def _aggregate_tool_calls(
        self, chunks: list, raw_events: list[dict[str, Any]]
    ) -> list[ToolCall]:
        """Extract tool calls from Google streaming events."""
        tool_calls: list[ToolCall] = []
        for event in raw_events:
            for candidate in event.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if "functionCall" in part:
                        kwargs: dict[str, Any] = {}
                        if "thoughtSignature" in part:
                            kwargs["thoughtSignature"] = part["thoughtSignature"]
                        tool_calls.append(
                            ToolCall(
                                id=str(uuid4()),
                                name=part["functionCall"]["name"],
                                arguments=part["functionCall"].get("args", {}),
                                **kwargs,
                            )
                        )
        return tool_calls

    def _aggregate_signature(
        self, chunks: list, raw_events: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Extract thought parts with signatures from Google streaming events."""
        thought_parts: list[dict[str, Any]] = []
        for event in raw_events:
            for candidate in event.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    if part.get("thought") and "thoughtSignature" in part:
                        thought_parts.append(part)
        return thought_parts


class GoogleTextClient(GoogleGenerateContentClient, TextClient):
    """Google text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return GOOGLE_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """Initialize request from Google contents array format."""

        def content_to_parts(content: Any) -> list[dict[str, Any]]:
            """Convert message content to Google parts array."""
            parts: list[dict[str, Any]] = []
            for part in message_parts(content):
                if isinstance(part, TextPart):
                    parts.append({"text": part.text})
                elif isinstance(part, ImagePart):
                    parts.append(build_media_part(part.image))
                elif isinstance(part, VideoPart):
                    parts.append(build_media_part(part.video))
                elif isinstance(part, AudioPart):
                    parts.append(build_media_part(part.audio))
                elif isinstance(part, DocumentPart):
                    parts.append(build_media_part(part.document))
            return parts

        system_parts: list[dict[str, Any]] = []
        contents: list[dict[str, Any]] = []

        for msg in request_messages(
            prompt=inputs.prompt,
            messages=inputs.messages,
            image=inputs.image,
            video=inputs.video,
            audio=inputs.audio,
            document=inputs.document,
        ):
            if msg.role in {Role.SYSTEM, Role.DEVELOPER}:
                system_parts.extend(content_to_parts(msg.content))
            elif isinstance(msg, ToolResult):
                contents.append(
                    {
                        "role": "user",
                        "parts": [
                            {
                                "functionResponse": {
                                    "name": msg.name,
                                    "response": {"result": tool_result_object(msg)},
                                }
                            }
                        ],
                    }
                )
            else:
                role = "model" if msg.role == Role.ASSISTANT else msg.role
                sig_blocks = msg.signature
                msg_parts = list(sig_blocks) if sig_blocks else []
                msg_parts.extend(content_to_parts(msg.content))
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        part: dict[str, Any] = {
                            "functionCall": {
                                "name": tc.name,
                                "args": tc.arguments,
                            }
                        }
                        thought_sig = getattr(tc, "thoughtSignature", None)
                        if thought_sig:
                            part["thoughtSignature"] = thought_sig
                        msg_parts.append(part)
                contents.append({"role": role, "parts": msg_parts})

        result: dict[str, Any] = {"contents": contents}
        if system_parts:
            result["system_instruction"] = {"parts": system_parts}
        return result

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> TextContent:
        """Parse content from response."""
        candidates = super()._parse_content(response_data)
        parts = candidates[0].get("content", {}).get("parts", [])
        for p in parts:
            if p.get("thought"):
                continue
            text = p.get("text")
            if text is not None:
                return text
        return ""

    def _parse_reasoning(
        self, response_data: dict[str, Any]
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """Parse thought parts from Google response."""
        candidates = response_data.get("candidates", [])
        if not candidates:
            return None, []
        parts = candidates[0].get("content", {}).get("parts", [])
        reasoning_parts: list[str] = []
        signature_blocks: list[dict[str, Any]] = []
        for p in parts:
            if p.get("thought"):
                text = p.get("text", "")
                if text:
                    reasoning_parts.append(text)
                signature_blocks.append(p)
        text = "\n".join(reasoning_parts) if reasoning_parts else None
        return text, signature_blocks

    def _parse_grounding(self, response_data: dict[str, Any]) -> Grounding | None:
        """Extract Google grounding with text character offsets."""
        meta = parse_grounding_metadata(response_data)
        if meta is None:
            return None
        return map_grounding(meta, self._parse_content(response_data))

    def _parse_tool_calls(self, response_data: dict[str, Any]) -> list[ToolCall]:
        """Parse tool calls from Google response."""
        candidates = response_data.get("candidates", [])
        if not candidates:
            return []
        parts = candidates[0].get("content", {}).get("parts", [])
        tool_calls: list[ToolCall] = []
        for p in parts:
            if "functionCall" in p:
                kwargs: dict[str, Any] = {}
                if "thoughtSignature" in p:
                    kwargs["thoughtSignature"] = p["thoughtSignature"]
                tool_calls.append(
                    ToolCall(
                        id=str(uuid4()),
                        name=p["functionCall"]["name"],
                        arguments=p["functionCall"].get("args", {}),
                        **kwargs,
                    )
                )
        return tool_calls

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return GoogleTextStream


__all__ = ["GoogleTextClient", "GoogleTextStream"]
