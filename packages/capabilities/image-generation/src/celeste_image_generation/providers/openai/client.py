"""OpenAI client implementation for image generation."""

import base64
from typing import Any, Unpack

from celeste_openai.images.client import OpenAIImagesClient

from celeste.artifacts import ImageArtifact
from celeste.parameters import ParameterMapper
from celeste_image_generation.client import ImageGenerationClient
from celeste_image_generation.io import (
    ImageGenerationFinishReason,
    ImageGenerationInput,
    ImageGenerationUsage,
)
from celeste_image_generation.parameters import ImageGenerationParameters

from .parameters import OPENAI_PARAMETER_MAPPERS
from .streaming import OpenAIImageGenerationStream


class OpenAIImageGenerationClient(OpenAIImagesClient, ImageGenerationClient):
    """OpenAI client for image generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return OPENAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageGenerationInput) -> dict[str, Any]:
        """Initialize request from OpenAI API format."""
        request = {
            "model": self.model.id,
            "prompt": inputs.prompt,
            "n": 1,
        }

        if self.model.id in ("dall-e-2", "dall-e-3"):
            request["response_format"] = "b64_json"

        return request

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
        # Use mixin's _parse_content to get data array
        data = super()._parse_content(response_data)
        image_data = data[0]

        b64_json = image_data.get("b64_json")
        if b64_json:
            image_bytes = base64.b64decode(b64_json)
            return ImageArtifact(data=image_bytes)

        url = image_data.get("url")
        if url:
            return ImageArtifact(url=url)

        msg = "No image URL or base64 data in response"
        raise ValueError(msg)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> ImageGenerationFinishReason:
        """OpenAI Images API doesn't provide finish reasons."""
        return ImageGenerationFinishReason(reason=None)

    def _stream_class(self) -> type[OpenAIImageGenerationStream]:
        """Return the Stream class for this client."""
        return OpenAIImageGenerationStream


__all__ = ["OpenAIImageGenerationClient"]
