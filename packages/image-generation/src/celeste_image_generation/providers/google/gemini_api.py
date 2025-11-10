"""Gemini API adapter for Google image generation.

Pure data transformer for Gemini multimodal models (gemini-2.5-flash-image).
Handles request/response structure transformation only.
"""

from typing import Any

from celeste_image_generation.io import ImageGenerationUsage

from . import config


class GeminiImageAPIAdapter:
    """Adapter for Gemini multimodal API request/response transformation.

    Request format: contents[].parts[] + generationConfig.responseModalities + imageConfig
    Response format: candidates[].content.parts[].inlineData (camelCase in REST API)
    """

    def build_request(self, prompt: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Build Gemini API request structure.

        Args:
            prompt: Text prompt for image generation.
            parameters: Parameter dictionary (aspectRatio, etc.).

        Returns:
            Gemini-formatted request with contents[] and generationConfig.
        """
        return {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseModalities": ["Image"],
                "imageConfig": parameters,
            },
        }

    def parse_response(self, response_data: dict[str, Any]) -> dict[str, Any] | None:
        """Parse Gemini API response structure.

        Args:
            response_data: Raw API response.

        Returns:
            First part containing inlineData with base64 image, or None if blocked.
        """
        candidates = response_data.get("candidates", [])
        if not candidates:
            return None

        candidate = candidates[0]
        if candidate.get("finishReason") != "STOP":
            return None
        return candidate["content"]["parts"][0]["inlineData"]

    def parse_usage(self, response_data: dict[str, Any]) -> ImageGenerationUsage:
        """Parse usage from Gemini API response.

        Args:
            response_data: Raw API response.

        Returns:
            ImageGenerationUsage with token counts and generated_images count.
        """
        usage_metadata = response_data.get("usageMetadata", {})
        candidates = response_data.get("candidates", [])

        return ImageGenerationUsage(
            input_tokens=usage_metadata.get("promptTokenCount"),
            output_tokens=usage_metadata.get("candidatesTokenCount"),
            total_tokens=usage_metadata.get("totalTokenCount"),
            generated_images=len(candidates),
        )

    @staticmethod
    def endpoint(model_id: str) -> str:
        """Get endpoint for model."""
        return config.GEMINI_ENDPOINT.format(model_id=model_id)


__all__ = ["GeminiImageAPIAdapter"]
