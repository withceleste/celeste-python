"""OpenAI Images API client mixin.

Provides shared implementation for capabilities using the OpenAI Images API:
- image-generation (generations endpoint)
- image-edit (edits endpoint)
"""

from collections.abc import AsyncGenerator
from typing import Any, ClassVar

from celeste.artifacts import ImageArtifact
from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.exceptions import ConstraintViolationError
from celeste.io import FinishReason
from celeste.utils import build_data_url

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
        if image := request_body.pop("image", None):
            request_body["images"] = [image, *request_body.get("images", [])]
        if images := request_body.get("images"):
            if len(images) > 16:
                msg = (
                    "OpenAI edits accept at most 16 images, including the primary image"
                )
                raise ConstraintViolationError(msg)
            request_body["images"] = [
                {"image_url": build_data_url(image)}
                if isinstance(image, ImageArtifact)
                else image
                for image in images
            ]
        if mask := request_body.get("mask"):
            if not request_body.get("images"):
                msg = "An image mask requires a primary or reference image"
                raise ConstraintViolationError(msg)
            if isinstance(mask, ImageArtifact):
                request_body["mask"] = {"image_url": build_data_url(mask)}
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
        if request_body.get("images"):
            endpoint = config.OpenAIImagesEndpoint.CREATE_EDIT
        elif endpoint is None:
            endpoint = config.OpenAIImagesEndpoint.CREATE_IMAGE

        headers = await self._json_headers(extra_headers)

        response = await self.http_client.post(
            f"{config.BASE_URL}{endpoint}",
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
        """Make streaming request to OpenAI Images API."""
        if request_body.get("images"):
            endpoint = config.OpenAIImagesEndpoint.CREATE_EDIT
        elif endpoint is None:
            endpoint = config.OpenAIImagesEndpoint.CREATE_IMAGE

        if "partial_images" not in request_body:
            request_body["partial_images"] = 1

        headers = await self._json_headers(extra_headers)

        return self.http_client.stream_post(
            f"{config.BASE_URL}{endpoint}",
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
        usage_data = response_data.get("usage", {})
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
