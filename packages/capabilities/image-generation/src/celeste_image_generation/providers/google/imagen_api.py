"""Imagen API adapter for Google image generation.

Pure data transformer for Imagen models (imagen-3.x, imagen-4.x).
Handles request/response structure transformation only.
"""

from typing import Any

from celeste_image_generation.io import ImageGenerationUsage

from . import config


class ImagenAPIAdapter:
    """Adapter for Imagen API request/response transformation.

    Request format: instances[].prompt + parameters
    Response format: predictions[].bytesBase64Encoded
    """

    def build_request(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Build Imagen API request structure.

        Args:
            prompt: Text prompt for image generation.
            parameters: Parameter dictionary (aspectRatio, imageSize, etc.).

        Returns:
            Imagen-formatted request with instances[] and parameters.
        """
        return {
            "instances": [{"prompt": prompt}],
            "parameters": parameters,
        }

    def parse_response(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Parse Imagen API response structure.

        Args:
            response_data: Raw API response.

        Returns:
            First prediction containing bytesBase64Encoded and mimeType.
        """
        return response_data["predictions"][0]

    def parse_usage(self, response_data: dict[str, Any]) -> ImageGenerationUsage:
        """Parse usage from Imagen API response.

        Args:
            response_data: Raw API response.

        Returns:
            ImageGenerationUsage with generated_images count from predictions array.
        """
        predictions = response_data.get("predictions", [])
        return ImageGenerationUsage(
            generated_images=len(predictions),
        )

    @staticmethod
    def endpoint(model_id: str) -> str:
        """Get endpoint for model."""
        return config.IMAGEN_ENDPOINT.format(model_id=model_id)


__all__ = ["ImagenAPIAdapter"]
