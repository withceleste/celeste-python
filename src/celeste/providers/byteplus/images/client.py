"""BytePlus Images API client mixin."""

from collections.abc import AsyncIterator
from typing import Any

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config


class BytePlusImagesClient(APIMixin):
    """Mixin for BytePlus Images API capabilities.

    Provides shared implementation for all capabilities using the Images API:
    - _make_request() - HTTP POST to /api/v3/images/generations
    - _make_stream_request() - HTTP streaming to /api/v3/images/generations
    - _parse_usage() - Extract usage dict from response
    - _parse_content() - Extract images/data array from response
    - _parse_finish_reason() - Extract finish reason from response
    - _build_metadata() - Filter content fields and extract seed

    Usage:
        class BytePlusImageGenerationClient(BytePlusImagesClient, ImageGenerationClient):
            def _parse_content(self, response_data, **parameters):
                images = response_data.get("images", [])
                # Extract image from images[0] or data[0]...
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
        request_body["stream"] = streaming
        return request_body

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to BytePlus Images API endpoint."""
        if endpoint is None:
            endpoint = config.BytePlusImagesEndpoint.CREATE_IMAGE

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
        """Make streaming request to BytePlus Images API endpoint."""
        if endpoint is None:
            endpoint = config.BytePlusImagesEndpoint.CREATE_IMAGE

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        return self.http_client.stream_post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map BytePlus Images usage fields to unified names.

        Shared by client and streaming across all capabilities.
        """
        return {
            UsageField.TOTAL_TOKENS: usage_data.get("total_tokens"),
            UsageField.OUTPUT_TOKENS: usage_data.get("output_tokens"),
            UsageField.NUM_IMAGES: usage_data.get("generated_images"),
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from Images API response.

        Returns dict that capability clients wrap in their specific Usage type.
        """
        usage_data = response_data.get("usage", {})
        return BytePlusImagesClient.map_usage_fields(usage_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse images/data array from Images API response.

        Returns raw images/data array that capability clients extract from.
        """
        images = response_data.get("images", [])
        if images:
            return images

        data = response_data.get("data", [])
        if data:
            return data

        msg = "No images or data in response"
        raise ValueError(msg)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """BytePlus doesn't provide finish reasons for image generation."""
        return FinishReason(reason=None)

    def _build_metadata(self, response_data: dict[str, Any]) -> Any:
        """Build metadata dictionary, extracting seed if present."""
        # Filter content fields before calling super
        content_fields = {"images", "data"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        metadata = super()._build_metadata(filtered_data)

        # Add provider-specific parsed fields
        seed = response_data.get("seed")
        if seed is not None:
            metadata["seed"] = seed

        return metadata


__all__ = ["BytePlusImagesClient"]
