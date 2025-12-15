"""BFL client implementation for image generation."""

from typing import Any, Unpack

from celeste_bfl.images.client import BFLImagesClient

from celeste.artifacts import ImageArtifact
from celeste.exceptions import ValidationError
from celeste.parameters import ParameterMapper
from celeste_image_generation.client import ImageGenerationClient
from celeste_image_generation.io import (
    ImageGenerationFinishReason,
    ImageGenerationInput,
    ImageGenerationUsage,
)
from celeste_image_generation.parameters import ImageGenerationParameters

from .parameters import BFL_PARAMETER_MAPPERS


class BFLImageGenerationClient(BFLImagesClient, ImageGenerationClient):
    """BFL client for image generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return BFL_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageGenerationInput) -> dict[str, Any]:
        """Initialize request for BFL API format."""
        return {
            "prompt": inputs.prompt,
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
        result = response_data.get("result", {})
        sample_url = result.get("sample")

        if not sample_url:
            msg = f"No image URL in {self.provider} response"
            raise ValidationError(msg)

        return ImageArtifact(url=sample_url)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> ImageGenerationFinishReason:
        """Parse finish reason from response."""
        status = response_data.get("status")
        if status == "Ready":
            return ImageGenerationFinishReason(reason="COMPLETE")
        elif status in ("Error", "Failed"):
            error_msg = response_data.get("error", "Generation failed")
            return ImageGenerationFinishReason(reason="ERROR", message=error_msg)
        return ImageGenerationFinishReason(reason=None)


__all__ = ["BFLImageGenerationClient"]
