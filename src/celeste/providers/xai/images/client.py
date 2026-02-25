"""xAI Images API client mixin."""

from collections.abc import AsyncIterator
from typing import Any, ClassVar

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason

from . import config


class XAIImagesClient(APIMixin):
    """Mixin for xAI Images API.

    Provides shared HTTP implementation:
    - _make_request(endpoint=...) - HTTP POST to specified endpoint
    - _make_stream_request() - Raises StreamingNotSupportedError (xAI Images doesn't support streaming)
    - _parse_usage() - Extract usage dict from response
    - _parse_content() - Extract data array from response
    - _parse_finish_reason() - Returns None (no finish reasons for images)
    - _content_fields: ClassVar - Content field names to exclude from metadata

    Modality clients pass endpoint parameter to route operations:
        await self._predict(inputs, endpoint=config.XAIImagesEndpoint.CREATE_IMAGE, **parameters)
    """

    _content_fields: ClassVar[set[str]] = {"data"}

    def _build_request(
        self,
        inputs: Any,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Build request with model ID."""
        request_body = super()._build_request(
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )
        request_body["model"] = self.model.id
        return request_body

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to xAI Images API."""
        if endpoint is None:
            endpoint = config.XAIImagesEndpoint.CREATE_IMAGE

        headers = self._json_headers(extra_headers)

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
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """xAI Images does not support SSE streaming."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map xAI Images usage fields to unified names."""
        return {
            UsageField.INPUT_TOKENS: usage_data.get("input_tokens"),
            UsageField.OUTPUT_TOKENS: usage_data.get("output_tokens"),
            UsageField.TOTAL_TOKENS: usage_data.get("total_tokens"),
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from xAI Images API response."""
        usage_data = response_data.get("usage", {})
        return XAIImagesClient.map_usage_fields(usage_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse data array from xAI Images API response."""
        data = response_data.get("data", [])
        if not data:
            msg = "No image data in response"
            raise ValueError(msg)
        return data

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """xAI Images API doesn't provide finish reasons."""
        return FinishReason(reason=None)


__all__ = ["XAIImagesClient"]
