"""OpenAI Audio API client mixin."""

from collections.abc import AsyncIterator
from typing import Any

from celeste.artifacts import AudioArtifact
from celeste.client import APIMixin
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason
from celeste.mime_types import AudioMimeType
from celeste.utils import detect_mime_type

from . import config

_MIME_TO_EXT: dict[str, str] = {
    AudioMimeType.MP3: "mp3",
    AudioMimeType.M4A: "m4a",
    AudioMimeType.WAV: "wav",
    AudioMimeType.WEBM: "webm",
    AudioMimeType.OGG: "ogg",
}


class OpenAIAudioClient(APIMixin):
    """Mixin for OpenAI Audio API speech and transcription."""

    def _build_request(
        self,
        inputs: Any,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Build request with model ID; default json response for transcription."""
        request_body = super()._build_request(
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )
        request_body["model"] = self.model.id
        if "file" in request_body:
            request_body.setdefault("response_format", "json")
        elif streaming:
            request_body["stream"] = True
        return request_body

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """OpenAI Audio speech endpoint does not support SSE streaming in this client."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """POST speech (JSON/binary) or transcription (multipart/JSON)."""
        _ = parameters
        if endpoint is None:
            endpoint = config.OpenAIAudioEndpoint.CREATE_SPEECH

        if endpoint == config.OpenAIAudioEndpoint.CREATE_TRANSCRIPTION:
            return await self._make_transcription_request(
                request_body, endpoint=endpoint, extra_headers=extra_headers
            )

        headers = self._json_headers(extra_headers)
        response = await self.http_client.post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )
        self._handle_error_response(response)
        return {
            "audio_bytes": response.content,
            "headers": dict(response.headers),
        }

    async def _make_transcription_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str,
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make multipart transcription request to OpenAI Audio API."""
        audio = request_body.pop("file")
        if not isinstance(audio, AudioArtifact):
            msg = "OpenAI transcription requires a single AudioArtifact"
            raise ValueError(msg)

        audio_bytes = audio.get_bytes()
        mime = audio.mime_type or detect_mime_type(audio_bytes)
        mime_str = mime.value if mime else "application/octet-stream"
        ext = _MIME_TO_EXT.get(mime, "wav") if mime is not None else "wav"

        files = {"file": (f"audio.{ext}", audio_bytes, mime_str)}
        data: dict[str, str] = {"model": str(request_body.pop("model"))}
        for key, value in request_body.items():
            if value is not None:
                data[key] = str(value)

        response = await self.http_client.post_multipart(
            f"{config.BASE_URL}{endpoint}",
            headers=self._merge_headers(self.auth.get_headers(), extra_headers),
            files=files,
            data=data,
        )
        self._handle_error_response(response)
        result: dict[str, Any] = response.json()
        return result

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map OpenAI Audio usage fields to unified names."""
        usage = usage_data.get("usage")
        if not isinstance(usage, dict):
            return {}
        if usage.get("type") == "duration":
            # Duration-only usage is kept in metadata; TextUsage has no seconds field.
            return {}
        mapped: dict[str, int | float | None] = {}
        for src, dst in (
            ("input_tokens", "input_tokens"),
            ("output_tokens", "output_tokens"),
            ("total_tokens", "total_tokens"),
        ):
            if src in usage:
                mapped[dst] = usage[src]
        return mapped

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from Audio API response."""
        return OpenAIAudioClient.map_usage_fields(response_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse transcript text; speech responses are handled by the modality client."""
        text = response_data.get("text")
        if text is not None:
            return str(text)
        msg = "OpenAI TTS returns binary responses; modality client must override generate()"
        raise NotImplementedError(msg)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """OpenAI Audio API doesn't provide finish reasons."""
        _ = response_data
        return FinishReason(reason=None)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Keep language, duration, and duration usage in metadata when present."""
        metadata = super()._build_metadata(response_data)
        for key in ("language", "duration"):
            if key in response_data:
                metadata[key] = response_data[key]
        usage = response_data.get("usage")
        if (
            isinstance(usage, dict)
            and usage.get("type") == "duration"
            and "seconds" in usage
        ):
            metadata.setdefault("duration", usage["seconds"])
        return metadata

    def _map_response_format_to_mime_type(
        self, response_format: str | None
    ) -> AudioMimeType:
        """Map OpenAI response_format to AudioMimeType."""
        format_map: dict[str, AudioMimeType] = {
            "mp3": AudioMimeType.MP3,
            "opus": AudioMimeType.OGG,
            "aac": AudioMimeType.AAC,
            "flac": AudioMimeType.FLAC,
            "wav": AudioMimeType.WAV,
            "pcm": AudioMimeType.WAV,
        }
        return format_map.get(response_format or "", AudioMimeType.MP3)


__all__ = ["OpenAIAudioClient"]
