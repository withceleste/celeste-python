"""Google Imagen API client mixin."""

from collections.abc import AsyncIterator
from typing import Any

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config


class GoogleImagenClient(APIMixin):
    """Mixin for Imagen API capabilities.

    Provides shared implementation for capabilities using the Imagen API:
    - _make_request() - HTTP POST to :predict endpoint
    - _parse_usage() - Returns empty dict (Imagen doesn't provide usage)
    - _parse_content() - Extract predictions[] array
    - _parse_finish_reason() - Returns None (Imagen doesn't provide finish reasons)
    - _build_metadata() - Filter out predictions content

    Capability clients extend parsing methods via super() to wrap/transform results.

    Usage:
        class GoogleImageGenerationClient(GoogleImagenClient, ImageGenerationClient):
            def _parse_content(self, response_data, **parameters):
                predictions = super()._parse_content(response_data)
                # Extract image from predictions[0]...
    """

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to Imagen :predict endpoint."""
        if endpoint is None:
            endpoint = config.GoogleImagenEndpoint.CREATE_IMAGE
        endpoint = endpoint.format(model_id=self.model.id)

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

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
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

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata, filtering out predictions content.

        Keeps metadata like raiFilteredReason, safety attributes.
        """
        content_fields = {"predictions"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)


__all__ = ["GoogleImagenClient"]
