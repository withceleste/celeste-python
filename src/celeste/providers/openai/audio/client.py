"""OpenAI Audio API client mixin."""

from collections.abc import AsyncIterator
from typing import Any

from celeste.client import APIMixin
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType, AudioMimeType

from . import config


class OpenAIAudioClient(APIMixin):
    """Mixin for OpenAI Audio API speech generation.

    Provides shared implementation for speech generation:
    - _make_request() - HTTP POST to /v1/audio/speech
    - _parse_usage() - Returns empty dict (Audio API doesn't return usage in body)
    - _map_response_format_to_mime_type() - Map format string to AudioMimeType

    The Audio API speech endpoint returns binary audio data, not JSON.
    Capability clients must handle the binary response in their generate() override.

    Usage:
        class OpenAISpeechGenerationClient(OpenAIAudioClient, SpeechGenerationClient):
            async def generate(self, *args, **parameters):
                # Handle binary response...
    """

    def _build_request(
        self,
        inputs: Any,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Build request with model ID and streaming flag."""
        request_body = super()._build_request(
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )
        request_body["model"] = self.model.id
        if streaming:
            request_body["stream"] = True
        return request_body

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """OpenAI Audio API speech endpoint does not support SSE streaming in this client."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to OpenAI Audio API speech endpoint.

        Returns dict with binary audio content.
        """
        if endpoint is None:
            endpoint = config.OpenAIAudioEndpoint.CREATE_SPEECH

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

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

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map OpenAI Audio usage fields to unified names.

        Shared by client and streaming across all capabilities.
        Audio API speech endpoint doesn't return usage in response body.
        Usage may be available in response headers or streaming events.
        """
        return {}

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from Audio API response."""
        return OpenAIAudioClient.map_usage_fields(response_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse content from OpenAI Audio API response.

        The speech endpoint returns binary audio, so base generate() should not call this.
        """
        msg = "OpenAI TTS returns binary responses; capability client must override generate()"
        raise NotImplementedError(msg)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """OpenAI Audio API doesn't provide finish reasons."""
        return FinishReason(reason=None)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary, filtering out content fields."""
        return super()._build_metadata(response_data)

    def _map_response_format_to_mime_type(
        self, response_format: str | None
    ) -> AudioMimeType:
        """Map OpenAI response_format to AudioMimeType.

        Supported formats: mp3, opus, aac, flac, wav, pcm.
        """
        format_map: dict[str, AudioMimeType] = {
            "mp3": AudioMimeType.MP3,
            "opus": AudioMimeType.OGG,  # Opus is typically in OGG container
            "aac": AudioMimeType.AAC,
            "flac": AudioMimeType.FLAC,
            "wav": AudioMimeType.WAV,
            "pcm": AudioMimeType.WAV,  # PCM is raw, closest match is WAV
        }
        return format_map.get(response_format or "", AudioMimeType.MP3)


__all__ = ["OpenAIAudioClient"]
