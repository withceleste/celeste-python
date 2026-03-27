"""Google text client (modality)."""

from typing import Any
from uuid import uuid4

from celeste.parameters import ParameterMapper
from celeste.providers.google.generate_content.client import GoogleGenerateContentClient
from celeste.providers.google.generate_content.streaming import (
    GoogleGenerateContentStream as _GoogleGenerateContentStream,
)
from celeste.providers.google.utils import build_media_part
from celeste.tools import ToolCall, ToolResult
from celeste.types import TextContent

from ...client import TextClient
from ...io import TextInput
from ...streaming import TextStream
from .parameters import GOOGLE_PARAMETER_MAPPERS


class GoogleTextStream(_GoogleGenerateContentStream, TextStream):
    """Google streaming for text modality."""

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


class GoogleTextClient(GoogleGenerateContentClient, TextClient):
    """Google text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return GOOGLE_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """Initialize request from Google contents array format."""
        # If messages provided, use them with special handling for system/developer
        if inputs.messages is not None:

            def normalize_part(part: Any) -> dict[str, Any]:
                """Normalize a content part to Google's format."""
                if isinstance(part, str):
                    return {"text": part}
                if isinstance(part, dict):
                    return part
                return {"text": str(part)}

            def content_to_parts(content: Any) -> list[dict[str, Any]]:
                """Convert message content to Google parts array."""
                if isinstance(content, str):
                    return [{"text": content}]
                if isinstance(content, list):
                    return [normalize_part(p) for p in content]
                return [normalize_part(content)]

            system_parts: list[dict[str, Any]] = []
            contents: list[dict[str, Any]] = []

            for msg in inputs.messages:
                if msg.role in ("system", "developer"):
                    system_parts.extend(content_to_parts(msg.content))
                elif isinstance(msg, ToolResult):
                    contents.append(
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "functionResponse": {
                                        "name": msg.name,
                                        "response": {"result": msg.content},
                                    }
                                }
                            ],
                        }
                    )
                else:
                    role = "model" if msg.role == "assistant" else msg.role
                    msg_parts = content_to_parts(msg.content)
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

        # Fall back to prompt-based input
        parts: list[dict[str, Any]] = []

        if inputs.image is not None:
            images = inputs.image if isinstance(inputs.image, list) else [inputs.image]
            for img in images:
                parts.append(build_media_part(img))

        if inputs.video is not None:
            videos = inputs.video if isinstance(inputs.video, list) else [inputs.video]
            for vid in videos:
                parts.append(build_media_part(vid))

        if inputs.audio is not None:
            audios = inputs.audio if isinstance(inputs.audio, list) else [inputs.audio]
            for aud in audios:
                parts.append(build_media_part(aud))

        parts.append({"text": inputs.prompt or ""})

        return {"contents": [{"role": "user", "parts": parts}]}

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
