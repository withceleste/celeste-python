"""Google text client (modality)."""

import base64
from typing import Any, Unpack
from uuid import uuid4

from celeste.artifacts import AudioArtifact, ImageArtifact, VideoArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.google.generate_content import config as google_config
from celeste.providers.google.generate_content.client import GoogleGenerateContentClient
from celeste.providers.google.generate_content.streaming import (
    GoogleGenerateContentStream as _GoogleGenerateContentStream,
)
from celeste.tools import ToolCall, ToolResult
from celeste.types import AudioContent, ImageContent, Message, TextContent, VideoContent
from celeste.utils import detect_mime_type

from ...client import TextClient
from ...io import (
    TextInput,
    TextOutput,
)
from ...parameters import TextParameters
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
                        tool_calls.append(
                            ToolCall(
                                id=str(uuid4()),
                                name=part["functionCall"]["name"],
                                arguments=part["functionCall"].get("args", {}),
                            )
                        )
        return tool_calls


class GoogleTextClient(GoogleGenerateContentClient, TextClient):
    """Google text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return GOOGLE_PARAMETER_MAPPERS

    async def generate(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Generate text from prompt."""
        inputs = TextInput(prompt=prompt, messages=messages)
        return await self._predict(
            inputs,
            endpoint=google_config.GoogleGenerateContentEndpoint.GENERATE_CONTENT,
            **parameters,
        )

    async def analyze(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        image: ImageContent | None = None,
        video: VideoContent | None = None,
        audio: AudioContent | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Analyze image(s), video(s), or audio with prompt or messages."""
        inputs = TextInput(
            prompt=prompt,
            messages=messages,
            image=image,
            video=video,
            audio=audio,
        )
        return await self._predict(
            inputs,
            endpoint=google_config.GoogleGenerateContentEndpoint.GENERATE_CONTENT,
            **parameters,
        )

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
                    contents.append(
                        {"role": role, "parts": content_to_parts(msg.content)}
                    )

            result: dict[str, Any] = {"contents": contents}
            if system_parts:
                result["system_instruction"] = {"parts": system_parts}
            return result

        # Fall back to prompt-based input
        parts: list[dict[str, Any]] = []

        if inputs.image is not None:
            images = inputs.image if isinstance(inputs.image, list) else [inputs.image]
            for img in images:
                parts.append(self._build_image_part(img))

        if inputs.video is not None:
            videos = inputs.video if isinstance(inputs.video, list) else [inputs.video]
            for vid in videos:
                parts.append(self._build_video_part(vid))

        if inputs.audio is not None:
            audios = inputs.audio if isinstance(inputs.audio, list) else [inputs.audio]
            for aud in audios:
                parts.append(self._build_audio_part(aud))

        parts.append({"text": inputs.prompt or ""})

        return {"contents": [{"role": "user", "parts": parts}]}

    def _build_image_part(self, image: ImageArtifact) -> dict[str, Any]:
        """Build a Gemini part from an ImageArtifact."""
        if image.url:
            return {"file_data": {"file_uri": image.url}}

        image_bytes = image.get_bytes()
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        mime = image.mime_type or detect_mime_type(image_bytes)
        mime_str = mime.value if mime else None

        return {"inline_data": {"mime_type": mime_str, "data": b64}}

    def _build_video_part(self, video: VideoArtifact) -> dict[str, Any]:
        """Build a Gemini part from a VideoArtifact."""
        if video.url:
            return {"file_data": {"file_uri": video.url}}

        video_bytes = video.get_bytes()
        b64 = base64.b64encode(video_bytes).decode("utf-8")
        mime = video.mime_type or detect_mime_type(video_bytes)
        mime_str = mime.value if mime else None

        return {"inline_data": {"mime_type": mime_str, "data": b64}}

    def _build_audio_part(self, audio: AudioArtifact) -> dict[str, Any]:
        """Build a Gemini part from an AudioArtifact."""
        if audio.url:
            return {"file_data": {"file_uri": audio.url}}

        audio_bytes = audio.get_bytes()
        b64 = base64.b64encode(audio_bytes).decode("utf-8")
        mime = audio.mime_type or detect_mime_type(audio_bytes)
        mime_str = mime.value if mime else None

        return {"inline_data": {"mime_type": mime_str, "data": b64}}

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[TextParameters],
    ) -> TextContent:
        """Parse content from response."""
        candidates = super()._parse_content(response_data)
        parts = candidates[0].get("content", {}).get("parts", [])
        text = parts[0].get("text") if parts else ""
        return text or ""

    def _parse_tool_calls(self, response_data: dict[str, Any]) -> list[ToolCall]:
        """Parse tool calls from Google response."""
        candidates = response_data.get("candidates", [])
        if not candidates:
            return []
        parts = candidates[0].get("content", {}).get("parts", [])
        return [
            ToolCall(
                id=str(uuid4()),
                name=p["functionCall"]["name"],
                arguments=p["functionCall"].get("args", {}),
            )
            for p in parts
            if "functionCall" in p
        ]

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return GoogleTextStream


__all__ = ["GoogleTextClient", "GoogleTextStream"]
