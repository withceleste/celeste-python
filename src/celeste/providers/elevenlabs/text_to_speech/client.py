"""ElevenLabs TextToSpeech API client mixin."""

from collections.abc import AsyncIterator
from typing import Any

import httpx

from celeste.client import APIMixin
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType, AudioMimeType

from . import config


class ElevenLabsTextToSpeechClient(APIMixin):
    """Mixin for ElevenLabs Text-to-Speech API.

    Provides shared implementation for speech generation:
    - _make_request() - HTTP POST to /v1/text-to-speech/{voice_id}
    - _make_stream_request() - HTTP streaming with binary chunks
    - _parse_usage() - Returns empty dict (TTS doesn't return usage)
    - _map_output_format_to_mime_type() - Map format string to AudioMimeType

    The TTS endpoint returns binary audio data, not JSON.
    Capability clients must handle the binary response in their generate() override.

    Usage:
        class ElevenLabsSpeechGenerationClient(ElevenLabsTextToSpeechClient, SpeechGenerationClient):
            async def generate(self, *args, **parameters):
                # Handle binary response...
    """

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to ElevenLabs TTS endpoint.

        Returns dict with binary audio content.
        Voice ID is extracted from request_body["_voice_id"] and used in URL path.
        """
        # Extract voice_id from request_body (set by VoiceMapper)
        voice_id = request_body.pop("_voice_id", None)
        if voice_id is None:
            voice_id = parameters.get("voice", config.DEFAULT_VOICE_ID)

        # Set model_id
        request_body["model_id"] = self.model.id

        # Build URL with voice_id in path
        if endpoint is None:
            endpoint = config.ElevenLabsTextToSpeechEndpoint.CREATE_SPEECH
        endpoint = endpoint.format(voice_id=voice_id)

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

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Make HTTP streaming request returning binary audio chunks.

        ElevenLabs streams binary audio data, not JSON SSE events.
        We wrap the binary stream to yield dicts compatible with Stream interface.
        """
        # Extract voice_id from request_body
        voice_id = request_body.pop("_voice_id", None)
        if voice_id is None:
            voice_id = parameters.get("voice", config.DEFAULT_VOICE_ID)

        # Set model_id
        request_body["model_id"] = self.model.id

        # Build URL with voice_id in path
        if endpoint is None:
            endpoint = config.ElevenLabsTextToSpeechEndpoint.STREAM_SPEECH
        endpoint = endpoint.format(voice_id=voice_id)

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        return self._stream_binary_audio(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )

    async def _stream_binary_audio(
        self,
        url: str,
        headers: dict[str, str],
        json_body: dict[str, Any],
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream binary audio data and yield as dict events.

        Wraps httpx streaming to yield dicts compatible with Stream interface.
        """
        client = await self.http_client._get_client()

        async with client.stream(
            "POST",
            url,
            json=json_body,
            headers=headers,
        ) as response:
            if not response.is_success:
                error_text = await response.aread()
                msg = f"HTTP {response.status_code}: {error_text.decode('utf-8', errors='ignore')}"
                raise httpx.HTTPStatusError(
                    msg,
                    request=response.request,
                    response=response,
                )

            async for chunk in response.aiter_bytes():
                if chunk:
                    yield {"data": chunk}

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map ElevenLabs usage fields to unified names.

        Shared by client and streaming across all capabilities.
        ElevenLabs TTS doesn't return usage in response body.
        """
        return {}

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from ElevenLabs TTS response."""
        return ElevenLabsTextToSpeechClient.map_usage_fields(response_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse content from ElevenLabs TTS response.

        The TTS endpoint returns binary audio, so base generate() should not call this.
        """
        msg = "ElevenLabs TTS returns binary responses; capability client must override generate()"
        raise NotImplementedError(msg)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """ElevenLabs TTS doesn't provide finish reasons."""
        return FinishReason(reason=None)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary, filtering out content fields."""
        return super()._build_metadata(response_data)

    def _map_output_format_to_mime_type(
        self, output_format: str | None
    ) -> AudioMimeType:
        """Map ElevenLabs output_format to AudioMimeType.

        ElevenLabs format: {codec}_{sample_rate}_{bitrate} (e.g., mp3_44100_128)
        """
        if output_format is None:
            return AudioMimeType.MP3

        parts = output_format.split("_")
        if not parts:
            return AudioMimeType.MP3

        codec = parts[0].lower()
        codec_map: dict[str, AudioMimeType] = {
            "mp3": AudioMimeType.MP3,
            "pcm": AudioMimeType.PCM,
            "aac": AudioMimeType.AAC,
            "flac": AudioMimeType.FLAC,
        }
        return codec_map.get(codec, AudioMimeType.MP3)


__all__ = ["ElevenLabsTextToSpeechClient"]
