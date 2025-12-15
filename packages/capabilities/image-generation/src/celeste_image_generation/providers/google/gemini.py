"""Gemini client for Google image generation."""

import base64
from typing import Any, Unpack

from celeste_google.generate_content.client import GoogleGenerateContentClient

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


class GeminiImageGenerationClient(GoogleGenerateContentClient, ImageGenerationClient):
    """Google Gemini client for image generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        """Parameter mappers for Gemini image generation."""
        return []  # Parameter mapping handled by GoogleImageGenerationClient wrapper

    def _init_request(self, inputs: ImageGenerationInput) -> dict[str, Any]:
        """Initialize request for Gemini image generation."""
        return {
            "contents": [{"parts": [{"text": inputs.prompt}]}],
            "generationConfig": {
                "responseModalities": ["Image"],
                "imageConfig": {},
            },
        }

    def _parse_usage(self, response_data: dict[str, Any]) -> ImageGenerationUsage:
        """Parse usage from response."""
        usage = super()._parse_usage(response_data)
        candidates = response_data.get("candidates", [])
        return ImageGenerationUsage(**usage, num_images=len(candidates))

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> ImageArtifact | list[ImageArtifact]:
        """Parse content from response."""
        candidates = super()._parse_content(response_data)
        artifacts = []

        for candidate in candidates:
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            for part in parts:
                inline_data = part.get("inlineData", {})
                base64_data = inline_data.get("data")

                if base64_data:
                    mime_type = ImageMimeType(inline_data.get("mimeType", "image/png"))
                    image_bytes = base64.b64decode(base64_data)
                    artifacts.append(
                        ImageArtifact(data=image_bytes, mime_type=mime_type)
                    )

        if not artifacts:
            return ImageArtifact()

        if len(artifacts) == 1:
            return artifacts[0]

        return artifacts

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> ImageGenerationFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        candidates = response_data.get("candidates", [])
        finish_message = None
        if candidates:
            finish_message = candidates[0].get("finishMessage")
        return ImageGenerationFinishReason(
            reason=finish_reason.reason,
            message=finish_message,
        )


__all__ = ["GeminiImageGenerationClient"]
