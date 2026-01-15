"""Google Cloud TTS API client mixin."""

from collections.abc import AsyncIterator
from typing import Any

from celeste.client import APIMixin
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from ..auth import GoogleADC
from . import config


class GoogleCloudTTSClient(APIMixin):
    """Mixin for Cloud TTS API capabilities.

    Provides shared implementation for speech generation using Cloud TTS API:
    - _make_request() - HTTP POST to text:synthesize endpoint
    - _parse_content() - Extract base64 audio content (generic)

    Auth uses GoogleADC (Application Default Credentials), unlike Gemini API which uses API keys.
    This is set in model_post_init to override the default API key auth.

    Capability clients extend via super() to wrap results in artifacts:
        class GoogleSpeechGenerationClient(GoogleCloudTTSClient, SpeechGenerationClient):
            def _parse_content(self, response_data, **params):
                audio_b64 = super()._parse_content(response_data)  # Get base64 string
                audio_bytes = base64.b64decode(audio_b64)
                return AudioArtifact(data=audio_bytes, mime_type=..., ...)
    """

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Cloud TTS does not support SSE streaming in this client."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map Cloud TTS usage fields to unified names.

        Cloud TTS API doesn't provide usage metadata.
        """
        return {}

    def model_post_init(self, _context: Any) -> None:
        """Override auth to use ADC for Cloud TTS (not API key like Gemini)."""
        super().model_post_init(_context)  # type: ignore[misc]
        object.__setattr__(self, "auth", GoogleADC())

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to Cloud TTS synthesize endpoint."""
        if endpoint is None:
            endpoint = config.GoogleCloudTTSEndpoint.CREATE_SPEECH

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
        data: dict[str, Any] = response.json()
        return data

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Extract base64 audio content from response.

        Returns base64 string that capability clients decode and wrap in artifacts.
        """
        audio_content = response_data.get("audioContent")
        if not audio_content:
            msg = "No audioContent in response"
            raise ValueError(msg)
        return audio_content

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Cloud TTS API doesn't provide usage metadata."""
        return GoogleCloudTTSClient.map_usage_fields(response_data)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Cloud TTS API doesn't provide finish reasons."""
        return FinishReason(reason=None)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary, filtering out content fields."""
        content_fields = {"audioContent"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)


__all__ = ["GoogleCloudTTSClient"]
