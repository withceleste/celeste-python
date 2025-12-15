"""BytePlus client implementation for image generation."""

import base64
from typing import Any, Unpack

from celeste_byteplus.images.client import BytePlusImagesClient

from celeste.artifacts import ImageArtifact
from celeste.exceptions import ConstraintViolationError, ValidationError
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste_image_generation.client import ImageGenerationClient
from celeste_image_generation.io import (
    ImageGenerationFinishReason,
    ImageGenerationInput,
    ImageGenerationUsage,
)
from celeste_image_generation.parameters import ImageGenerationParameters

from .parameters import BYTEPLUS_PARAMETER_MAPPERS
from .streaming import BytePlusImageGenerationStream


class BytePlusImageGenerationClient(BytePlusImagesClient, ImageGenerationClient):
    """BytePlus client for image generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return BYTEPLUS_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageGenerationInput) -> dict[str, Any]:
        """Initialize request from BytePlus API structure."""
        return {
            "model": self.model.id,
            "prompt": inputs.prompt,
            "response_format": "url",
        }

    def _parse_usage(self, response_data: dict[str, Any]) -> ImageGenerationUsage:
        """Parse usage from response."""
        usage = super()._parse_usage(response_data)
        return ImageGenerationUsage(**usage)

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

        msg = "No image content found in BytePlus response"
        raise ValidationError(msg)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> ImageGenerationFinishReason:
        """Parse finish reason from response.

        BytePlus doesn't provide finish reasons for image generation.
        """
        return ImageGenerationFinishReason(reason=None)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> Any:
        """Make HTTP request with parameter validation."""
        # Validate mutually exclusive parameters
        if parameters.get("aspect_ratio") and parameters.get("quality"):
            msg = (
                "Cannot use both 'aspect_ratio' and 'quality' parameters. "
                "BytePlus's 'size' field supports two methods that cannot be combined:\n"
                "  • quality: Resolution class ('1K', '2K', '4K')\n"
                "  • aspect_ratio: Exact dimensions (e.g., '2048x2048', '3840x2160')\n"
                "Use one or the other, not both."
            )
            raise ConstraintViolationError(msg)

        return await super()._make_request(request_body, **parameters)

    def _stream_class(self) -> type[BytePlusImageGenerationStream]:
        """Return the Stream class for this client."""
        return BytePlusImageGenerationStream


__all__ = ["BytePlusImageGenerationClient"]
