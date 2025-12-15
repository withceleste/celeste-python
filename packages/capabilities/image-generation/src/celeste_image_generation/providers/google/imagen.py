"""Imagen client for Google image generation."""

import base64
from typing import Any, Unpack

from celeste_google.imagen.client import GoogleImagenClient

from celeste.artifacts import ImageArtifact
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste_image_generation.client import ImageGenerationClient
from celeste_image_generation.io import (
    ImageGenerationFinishReason,
    ImageGenerationInput,
    ImageGenerationUsage,
)
from celeste_image_generation.parameters import ImageGenerationParameters

from .imagen_parameters import IMAGEN_PARAMETER_MAPPERS


class ImagenImageGenerationClient(GoogleImagenClient, ImageGenerationClient):
    """Google Imagen client for image generation.

    Uses Imagen API format: instances[].prompt → predictions[].
    For Imagen models (imagen-3.x, imagen-4.x).
    """

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return IMAGEN_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageGenerationInput) -> dict[str, Any]:
        """Initialize request for Imagen API."""
        return {
            "instances": [{"prompt": inputs.prompt}],
            "parameters": {},
        }

    def _parse_usage(self, response_data: dict[str, Any]) -> ImageGenerationUsage:
        """Parse usage from response."""
        usage = super()._parse_usage(response_data)
        return ImageGenerationUsage(**usage)

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> ImageArtifact | list[ImageArtifact]:
        """Parse content from response.

        Returns ImageArtifact for single image, list[ImageArtifact] for multiple.
        """
        predictions = response_data.get("predictions", [])
        if not predictions:
            return ImageArtifact()

        images: list[ImageArtifact] = []
        for prediction in predictions:
            base64_data = prediction.get("bytesBase64Encoded")
            if base64_data:
                mime_type = ImageMimeType(prediction.get("mimeType", "image/png"))
                image_bytes = base64.b64decode(base64_data)
                images.append(ImageArtifact(data=image_bytes, mime_type=mime_type))

        # Return type logic:
        # - num_images=1 explicitly → single ImageArtifact
        # - num_images>1 explicitly → list (even if fewer returned)
        # - num_images=None (not specified) → based on actual count returned
        num_images_requested = parameters.get("num_images")
        if num_images_requested == 1:
            return images[0] if images else ImageArtifact()
        if num_images_requested is not None and num_images_requested > 1:
            return images if images else []
        # Not specified: return based on what provider actually returned
        if len(images) == 1:
            return images[0]
        return images if images else ImageArtifact()

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> ImageGenerationFinishReason:
        """Parse finish reason from response.

        Imagen API doesn't provide finish reasons.
        """
        return ImageGenerationFinishReason(reason=None)


__all__ = ["ImagenImageGenerationClient"]
