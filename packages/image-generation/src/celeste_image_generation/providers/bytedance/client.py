"""ByteDance client implementation for image generation."""

import base64
from collections.abc import AsyncIterator
from typing import Any, Unpack

import httpx

from celeste.artifacts import ImageArtifact
from celeste.exceptions import ConstraintViolationError, ValidationError
from celeste.mime_types import ApplicationMimeType, ImageMimeType
from celeste.parameters import ParameterMapper
from celeste_image_generation.client import ImageGenerationClient
from celeste_image_generation.io import (
    ImageGenerationFinishReason,
    ImageGenerationInput,
    ImageGenerationUsage,
)
from celeste_image_generation.parameters import ImageGenerationParameters

from . import config
from .parameters import BYTEDANCE_PARAMETER_MAPPERS
from .streaming import ByteDanceImageGenerationStream


class ByteDanceImageGenerationClient(ImageGenerationClient):
    """ByteDance client for image generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return BYTEDANCE_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageGenerationInput) -> dict[str, Any]:
        """Initialize request from ByteDance API structure."""
        return {
            "model": self.model.id,
            "prompt": inputs.prompt,
            "response_format": "url",
        }

    def _parse_usage(self, response_data: dict[str, Any]) -> ImageGenerationUsage:
        """Parse usage from response."""
        usage_data = response_data.get("usage", {})

        return ImageGenerationUsage(
            total_tokens=usage_data.get("total_tokens"),
            output_tokens=usage_data.get("output_tokens"),
            generated_images=usage_data.get("generated_images"),
        )

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> ImageArtifact:
        """Parse content from response."""
        images = response_data.get("images", [])
        if images and images[0].get("url"):
            return ImageArtifact(
                url=images[0]["url"],
                mime_type=ImageMimeType.PNG,
            )

        data = response_data.get("data", [])
        if data:
            if data[0].get("url"):
                return ImageArtifact(
                    url=data[0]["url"],
                    mime_type=ImageMimeType.PNG,
                )
            if data[0].get("b64_json"):
                image_bytes = base64.b64decode(data[0]["b64_json"])
                return ImageArtifact(
                    data=image_bytes,
                    mime_type=ImageMimeType.PNG,
                )

        msg = "No image content found in ByteDance response"
        raise ValidationError(msg)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> ImageGenerationFinishReason | None:
        """Parse finish reason from response.

        ByteDance doesn't provide finish reasons for image generation.
        """
        return None

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data.

        Extracts seed if present.
        """
        metadata = super()._build_metadata(response_data)
        # Add provider-specific parsed fields
        seed = response_data.get("seed")
        if seed is not None:
            metadata["seed"] = seed
        return metadata

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""
        # Validate mutually exclusive parameters
        if parameters.get("aspect_ratio") and parameters.get("quality"):
            msg = (
                "Cannot use both 'aspect_ratio' and 'quality' parameters. "
                "ByteDance's 'size' field supports two methods that cannot be combined:\n"
                "  • quality: Resolution class ('1K', '2K', '4K')\n"
                "  • aspect_ratio: Exact dimensions (e.g., '2048x2048', '3840x2160')\n"
                "Use one or the other, not both."
            )
            raise ConstraintViolationError(msg)

        request_body["stream"] = False

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

        return await self.http_client.post(
            f"{config.BASE_URL}{config.ENDPOINT}",
            headers=headers,
            json_body=request_body,
        )

    def _stream_class(self) -> type[ByteDanceImageGenerationStream]:
        """Return the Stream class for this client."""
        return ByteDanceImageGenerationStream

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> AsyncIterator[dict[str, Any]]:
        """Make HTTP streaming request and return async iterator of events."""
        request_body["stream"] = True

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

        return self.http_client.stream_post(
            f"{config.BASE_URL}{config.ENDPOINT}",
            headers=headers,
            json_body=request_body,
        )


__all__ = ["ByteDanceImageGenerationClient"]
