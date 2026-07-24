"""ElevenLabs Speech-to-Text API client mixin."""

from typing import Any, ClassVar

from celeste.artifacts import AudioArtifact
from celeste.client import APIMixin
from celeste.io import FinishReason
from celeste.mime_types import AudioMimeType
from celeste.utils import detect_mime_type

from . import config

_MIME_TO_EXT: dict[str, str] = {
    AudioMimeType.FLAC: "flac",
    AudioMimeType.MP3: "mp3",
    AudioMimeType.M4A: "m4a",
    AudioMimeType.OGG: "ogg",
    AudioMimeType.WAV: "wav",
    AudioMimeType.WEBM: "webm",
}


class ElevenLabsSpeechToTextClient(APIMixin):
    """Mixin for ElevenLabs Speech-to-Text API."""

    _content_fields: ClassVar[set[str]] = {"text", "words"}

    def _build_request(
        self,
        inputs: Any,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Build request with model_id."""
        _ = streaming
        request_body = super()._build_request(
            inputs, extra_body=extra_body, streaming=False, **parameters
        )
        request_body["model_id"] = self.model.id
        return request_body

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make multipart transcription request to ElevenLabs STT API."""
        _ = parameters
        if endpoint is None:
            endpoint = config.ElevenLabsSpeechToTextEndpoint.CREATE_TRANSCRIPTION

        audio = request_body.pop("file")
        if not isinstance(audio, AudioArtifact):
            msg = "ElevenLabs transcription requires a single AudioArtifact"
            raise ValueError(msg)

        audio_bytes = audio.get_bytes()
        mime = audio.mime_type or detect_mime_type(audio_bytes)
        mime_str = mime.value if mime else "application/octet-stream"
        ext = _MIME_TO_EXT.get(mime, "wav") if mime is not None else "wav"

        files = {"file": (f"audio.{ext}", audio_bytes, mime_str)}
        data: dict[str, str] = {"model_id": str(request_body.pop("model_id"))}
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

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """ElevenLabs STT does not return token usage in the body."""
        _ = response_data
        return {}

    def _parse_content(self, response_data: dict[str, Any]) -> str:
        """Parse transcript text from ElevenLabs STT response."""
        text = response_data.get("text")
        if text is None:
            msg = "No text in transcription response"
            raise ValueError(msg)
        return str(text)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """ElevenLabs STT does not provide finish reasons."""
        _ = response_data
        return FinishReason(reason=None)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Keep language fields in metadata when present."""
        metadata = super()._build_metadata(response_data)
        for key in ("language_code", "language_probability"):
            if key in response_data:
                metadata[key] = response_data[key]
        return metadata


__all__ = ["ElevenLabsSpeechToTextClient"]
