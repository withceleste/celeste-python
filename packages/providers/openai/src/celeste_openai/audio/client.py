"""OpenAI Audio API client with shared implementation."""

from typing import Any

import httpx

from celeste.client import APIMixin
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

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Any,
    ) -> httpx.Response:
        """Make HTTP request to OpenAI Audio API speech endpoint.

        Returns the raw response with binary audio content.
        """
        request_body["model"] = self.model.id

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        return await self.http_client.post(
            f"{config.BASE_URL}{config.OpenAIAudioEndpoint.CREATE_SPEECH}",
            headers=headers,
            json_body=request_body,
        )

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | None]:
        """Map OpenAI Audio usage fields to unified names.

        Shared by client and streaming across all capabilities.
        Audio API speech endpoint doesn't return usage in response body.
        Usage may be available in response headers or streaming events.
        """
        return {}

    def _parse_usage(self, response_data: dict[str, Any]) -> dict[str, int | None]:
        """Extract usage data from Audio API response."""
        return OpenAIAudioClient.map_usage_fields(response_data)

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
