"""OpenAI Images API client mixin.

Provides shared implementation for capabilities using the OpenAI Images API:
- image-generation (generations endpoint)
"""

from collections.abc import AsyncIterator
from typing import Any

import httpx

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config


class OpenAIImagesClient(APIMixin):
    """Mixin for OpenAI Images API image generation.

    Provides shared implementation for image generation:
    - _make_request() - HTTP POST to /v1/images/generations
    - _make_stream_request() - HTTP streaming to /v1/images/generations
    - _parse_usage() - Extract usage dict from response
    - _parse_content() - Extract data array from response
    - _parse_finish_reason() - Returns None (Images API doesn't provide finish reasons)
    - _build_metadata() - Filter content fields and include revised_prompt

    Usage:
        class OpenAIImageGenerationClient(OpenAIImagesClient, ImageGenerationClient):
            def _parse_content(self, response_data, **parameters):
                data = super()._parse_content(response_data)
                # Extract image from data[0]...
    """

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Any,
    ) -> httpx.Response:
        """Make HTTP request to OpenAI Images API generations endpoint."""
        request_body["model"] = self.model.id

        # DALL-E 2/3 need b64_json response format
        if self.model.id in ("dall-e-2", "dall-e-3"):
            request_body.setdefault("response_format", "b64_json")

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        return await self.http_client.post(
            f"{config.BASE_URL}{config.OpenAIImagesEndpoint.CREATE_IMAGE}",
            headers=headers,
            json_body=request_body,
        )

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Make streaming request to OpenAI Images API generations endpoint.

        Streaming is only supported for gpt-image-1.
        """
        request_body["model"] = self.model.id
        request_body["stream"] = True

        if "partial_images" not in request_body:
            request_body["partial_images"] = 1

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        return self.http_client.stream_post(
            f"{config.BASE_URL}{config.OpenAIImagesEndpoint.CREATE_IMAGE}",
            headers=headers,
            json_body=request_body,
        )

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | None]:
        """Map OpenAI Images usage fields to unified names.

        Shared by client and streaming across all capabilities.
        """
        return {
            UsageField.INPUT_TOKENS: usage_data.get("input_tokens"),
            UsageField.OUTPUT_TOKENS: usage_data.get("output_tokens"),
            UsageField.TOTAL_TOKENS: usage_data.get("total_tokens"),
        }

    def _parse_usage(self, response_data: dict[str, Any]) -> dict[str, int | None]:
        """Extract usage data from Images API response.

        Returns dict that capability clients wrap in their specific Usage type.
        gpt-image-1 returns usage, DALL-E models don't.
        """
        usage_data = response_data.get("usage", {})
        return OpenAIImagesClient.map_usage_fields(usage_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse data array from Images API response.

        Returns data array that capability clients extract images from.
        """
        data = response_data.get("data", [])
        if not data:
            msg = "No image data in response"
            raise ValueError(msg)
        return data

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Images API doesn't provide finish reasons."""
        return FinishReason(reason=None)

    def _build_metadata(self, response_data: dict[str, Any]) -> Any:
        """Build metadata dictionary, including revised_prompt if present."""
        content_fields = {"data"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }

        metadata = super()._build_metadata(filtered_data)

        return metadata


__all__ = ["OpenAIImagesClient"]
