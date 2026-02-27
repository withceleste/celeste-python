"""Google Imagen API client mixin."""

from collections.abc import AsyncIterator
from typing import Any, ClassVar

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason

from ..auth import GoogleADC
from . import config


class GoogleImagenClient(APIMixin):
    """Mixin for Imagen API capabilities.

    Provides shared implementation for capabilities using the Imagen API:
    - _make_request() - HTTP POST to :predict endpoint
    - _parse_usage() - Returns empty dict (Imagen doesn't provide usage)
    - _parse_content() - Extract predictions[] array
    - _parse_finish_reason() - Returns None (Imagen doesn't provide finish reasons)
    - _content_fields: ClassVar - Content field names to exclude from metadata

    Auth-based endpoint selection:
    - GoogleADC auth -> Vertex AI endpoints
    - API key auth -> Gemini API endpoints

    Capability clients extend parsing methods via super() to wrap/transform results.

    Usage:
        class GoogleImageGenerationClient(GoogleImagenClient, ImageGenerationClient):
            def _parse_content(self, response_data):
                predictions = super()._parse_content(response_data)
                # Extract image from predictions[0]...
    """

    _content_fields: ClassVar[set[str]] = {"predictions"}

    def _get_vertex_endpoint(self, gemini_endpoint: str) -> str:
        """Map Gemini Imagen endpoint to Vertex AI endpoint."""
        mapping: dict[str, str] = {
            config.GoogleImagenEndpoint.CREATE_IMAGE: config.VertexImagenEndpoint.CREATE_IMAGE,
        }
        vertex_endpoint = mapping.get(gemini_endpoint)
        if vertex_endpoint is None:
            raise ValueError(f"No Vertex AI endpoint mapping for: {gemini_endpoint}")
        return vertex_endpoint

    def _build_url(self, endpoint: str) -> str:
        """Build full URL based on auth type."""
        if isinstance(self.auth, GoogleADC):
            return self.auth.build_url(
                self._get_vertex_endpoint(endpoint), model_id=self.model.id
            )
        return f"{config.BASE_URL}{endpoint.format(model_id=self.model.id)}"

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to Imagen :predict endpoint."""
        if endpoint is None:
            endpoint = config.GoogleImagenEndpoint.CREATE_IMAGE

        headers = self._json_headers(extra_headers)
        response = await self.http_client.post(
            self._build_url(endpoint),
            headers=headers,
            json_body=request_body,
        )
        self._handle_error_response(response)
        data: dict[str, Any] = response.json()
        return data

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Imagen API does not support SSE streaming in this client."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map Google Imagen usage fields to unified names.

        Shared by client and streaming across all capabilities.
        Imagen API doesn't provide token usage, but we can extract num_images.
        """
        predictions = usage_data.get("predictions", [])
        return {
            UsageField.NUM_IMAGES: len(predictions),
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from Imagen API response."""
        predictions = response_data.get("predictions", [])
        return GoogleImagenClient.map_usage_fields({"predictions": predictions})

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse predictions from response.

        Returns predictions array that capability clients extract from.
        """
        predictions = response_data.get("predictions", [])
        if not predictions:
            msg = "No predictions in response"
            raise ValueError(msg)
        return predictions

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Imagen API doesn't provide finish reasons."""
        return FinishReason(reason=None)


__all__ = ["GoogleImagenClient"]
