"""OpenAI Images API client mixin.

Provides shared implementation for capabilities using the OpenAI Images API:
- image-generation (generations endpoint)
- image-edit (edits endpoint)
"""

from collections.abc import AsyncGenerator
from typing import Any, ClassVar

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.io import FinishReason

from . import config


class OpenAIImagesClient(APIMixin):
    """Mixin for OpenAI Images API.

    Provides shared implementation for image operations:
    - _make_request(endpoint=...) - HTTP POST to images endpoint
    - _make_stream_request() - HTTP streaming
    - _parse_usage() - Extract usage dict from response
    - _parse_content() - Extract data array from response
    - _parse_finish_reason() - Returns None (Images API doesn't provide finish reasons)
    - _content_fields: ClassVar - Content field names to exclude from metadata
    """

    _content_fields: ClassVar[set[str]] = {"data"}

    def _build_url(self, endpoint: str, streaming: bool = False) -> str:
        """Build the request URL, honoring an explicit base_url override."""
        base = self.base_url if self.base_url is not None else config.BASE_URL
        return f"{base.rstrip('/')}{endpoint}"

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

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to OpenAI Images API."""
        if endpoint is None:
            endpoint = config.OpenAIImagesEndpoint.CREATE_IMAGE

        # Input images are only accepted by the edits endpoint
        if "images" in request_body:
            endpoint = config.OpenAIImagesEndpoint.CREATE_EDIT

        return await self._make_json_request(
            request_body, endpoint, extra_headers=extra_headers
        )

    async def _make_json_request(
        self,
        request_body: dict[str, Any],
        endpoint: str,
        *,
        extra_headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make JSON request to an Images API endpoint."""
        headers = await self._json_headers(extra_headers)

        response = await self.http_client.post(
            self._build_url(endpoint),
            headers=headers,
            json_body=request_body,
        )
        self._handle_error_response(response)
        data: dict[str, Any] = response.json()
        return data

    async def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Make streaming request to OpenAI Images API.

        Streaming is only supported for gpt-image-1.
        """
        if endpoint is None:
            endpoint = config.OpenAIImagesEndpoint.CREATE_IMAGE

        if "partial_images" not in request_body:
            request_body["partial_images"] = 1

        # Input images are only accepted by the edits endpoint
        if "images" in request_body:
            endpoint = config.OpenAIImagesEndpoint.CREATE_EDIT

        headers = await self._json_headers(extra_headers)

        return self.http_client.stream_post(
            self._build_url(endpoint, streaming=True),
            headers=headers,
            json_body=request_body,
        )

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map OpenAI Images usage fields to unified names.

        Shared by client and streaming across all capabilities.
        """
        return {
            UsageField.INPUT_TOKENS: usage_data.get("input_tokens"),
            UsageField.OUTPUT_TOKENS: usage_data.get("output_tokens"),
            UsageField.TOTAL_TOKENS: usage_data.get("total_tokens"),
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from Images API response.

        Returns dict that modality clients wrap in their specific Usage type.
        gpt-image-1 returns usage, DALL-E models don't.
        """
        usage_data = response_data.get("usage") or {}
        return OpenAIImagesClient.map_usage_fields(usage_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse data array from Images API response.

        Returns data array that modality clients extract images from.
        """
        data = response_data.get("data", [])
        if not data:
            msg = "No image data in response"
            raise ValueError(msg)
        return data

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Images API doesn't provide finish reasons."""
        return FinishReason(reason=None)


__all__ = ["OpenAIImagesClient"]
