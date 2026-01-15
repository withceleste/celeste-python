"""OpenAI Images API client mixin.

Provides shared implementation for capabilities using the OpenAI Images API:
- image-generation (generations endpoint)
- image-edit (edits endpoint)
"""

from collections.abc import AsyncIterator
from typing import Any

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType
from celeste.utils import detect_mime_type

from . import config


class OpenAIImagesClient(APIMixin):
    """Mixin for OpenAI Images API.

    Provides shared implementation for image operations:
    - _make_request(endpoint=...) - HTTP POST to images endpoint
    - _make_stream_request() - HTTP streaming
    - _parse_usage() - Extract usage dict from response
    - _parse_content() - Extract data array from response
    - _parse_finish_reason() - Returns None (Images API doesn't provide finish reasons)
    - _build_metadata() - Filter content fields and include revised_prompt
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
        if streaming:
            request_body["stream"] = True
        return request_body

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to OpenAI Images API."""
        if endpoint is None:
            endpoint = config.OpenAIImagesEndpoint.CREATE_IMAGE

        # Edit endpoint requires multipart/form-data
        if endpoint == config.OpenAIImagesEndpoint.CREATE_EDIT:
            return await self._make_multipart_request(request_body, endpoint)

        # Generate uses JSON
        return await self._make_json_request(request_body, endpoint)

    async def _make_json_request(
        self,
        request_body: dict[str, Any],
        endpoint: str,
    ) -> dict[str, Any]:
        """Make JSON request for generate operations."""
        # DALL-E 2/3 need b64_json response format
        if self.model.id in ("dall-e-2", "dall-e-3"):
            request_body.setdefault("response_format", "b64_json")

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

    async def _make_multipart_request(
        self,
        request_body: dict[str, Any],
        endpoint: str,
    ) -> dict[str, Any]:
        """Make multipart request for edit operations."""
        image_artifact = request_body.pop("image")

        # Get image bytes from artifact
        image_bytes = image_artifact.get_bytes()

        # Detect MIME type if not explicitly set
        mime = image_artifact.mime_type or detect_mime_type(image_bytes)
        mime_str = mime.value if mime else "application/octet-stream"

        files = {"image": ("image", image_bytes, mime_str)}
        # Model is already in request_body from _build_request()
        model = request_body.pop("model")
        data = {"model": model}

        # Add remaining fields as form data
        for key, value in request_body.items():
            if value is not None:
                data[key] = str(value)

        response = await self.http_client.post_multipart(
            f"{config.BASE_URL}{endpoint}",
            headers=self.auth.get_headers(),
            files=files,
            data=data,
        )
        self._handle_error_response(response)
        response_data: dict[str, Any] = response.json()
        return response_data

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Make streaming request to OpenAI Images API generations endpoint.

        Streaming is only supported for gpt-image-1.
        """
        if endpoint is None:
            endpoint = config.OpenAIImagesEndpoint.CREATE_IMAGE

        if "partial_images" not in request_body:
            request_body["partial_images"] = 1

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
