"""Google Cloud TTS API client with shared implementation."""

from typing import Any

import httpx

from celeste.auth import get_auth_class
from celeste.client import APIMixin
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config


class GoogleCloudTTSClient(APIMixin):
    """Mixin for Cloud TTS API capabilities.

    Provides shared implementation for speech generation using Cloud TTS API:
    - model_post_init() - Override auth to use GoogleADC (Cloud TTS requires OAuth)
    - _make_request() - HTTP POST to text:synthesize endpoint
    - _parse_content() - Extract base64 audio content (generic)

    Capability clients extend via super() to wrap results in artifacts:
        class GoogleSpeechGenerationClient(GoogleCloudTTSClient, SpeechGenerationClient):
            def _parse_content(self, response_data, **params):
                audio_b64 = super()._parse_content(response_data)  # Get base64 string
                audio_bytes = base64.b64decode(audio_b64)
                return AudioArtifact(data=audio_bytes, mime_type=..., ...)
    """

    def model_post_init(self, __context: object) -> None:
        """Override auth to use OAuth/ADC (Cloud TTS requires it)."""
        super().model_post_init(__context)  # type: ignore[misc]
        GoogleADC = get_auth_class("google_adc")
        object.__setattr__(self, "auth", GoogleADC())

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Any,
    ) -> httpx.Response:
        """Make HTTP request to Cloud TTS synthesize endpoint."""
        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        return await self.http_client.post(
            f"{config.BASE_URL}{config.GoogleCloudTTSEndpoint.CREATE_SPEECH}",
            headers=headers,
            json_body=request_body,
        )

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Extract base64 audio content from response.

        Returns base64 string that capability clients decode and wrap in artifacts.
        """
        audio_content = response_data.get("audioContent")
        if not audio_content:
            msg = "No audioContent in response"
            raise ValueError(msg)
        return audio_content

    def _parse_usage(self, response_data: dict[str, Any]) -> dict[str, int | None]:
        """Cloud TTS API doesn't provide usage metadata."""
        return {}

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Cloud TTS API doesn't provide finish reasons."""
        return FinishReason(reason=None)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata, filtering out audio content."""
        content_fields = {"audioContent"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)


__all__ = ["GoogleCloudTTSClient"]
