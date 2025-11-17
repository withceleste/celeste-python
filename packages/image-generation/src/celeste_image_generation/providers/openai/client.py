"""OpenAI client implementation for image generation."""

import base64
from collections.abc import AsyncIterator
from typing import Any, Unpack

import httpx

from celeste.artifacts import ImageArtifact
from celeste.mime_types import ApplicationMimeType
from celeste.parameters import ParameterMapper
from celeste_image_generation.client import ImageGenerationClient
from celeste_image_generation.io import (
    ImageGenerationFinishReason,
    ImageGenerationInput,
    ImageGenerationUsage,
)
from celeste_image_generation.parameters import ImageGenerationParameters

from . import config
from .parameters import OPENAI_PARAMETER_MAPPERS
from .streaming import OpenAIImageGenerationStream


class OpenAIImageGenerationClient(ImageGenerationClient):
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
        return ImageGenerationUsage()

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> ImageArtifact:
        """Parse content from response."""
        data = response_data.get("data", [])
        if not data:
            msg = "No image data in response"
            raise ValueError(msg)

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
    ) -> ImageGenerationFinishReason | None:
        """Parse finish reason from response."""
        return None

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        metadata = super()._build_metadata(response_data)
        # Add provider-specific parsed fields
        if response_data.get("data") and response_data["data"]:
            revised_prompt = response_data["data"][0].get("revised_prompt")
            if revised_prompt:
                metadata["revised_prompt"] = revised_prompt
        return metadata

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""
        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

        return await self.http_client.post(
            f"{config.BASE_URL}{config.ENDPOINT}",
            headers=headers,
            json_body=request_body,
        )

    def _stream_class(self) -> type[OpenAIImageGenerationStream]:
        """Return the Stream class for this client."""
        return OpenAIImageGenerationStream

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> AsyncIterator[dict[str, Any]]:
        """Make HTTP streaming request and return async iterator of events."""
        if self.model.id != "gpt-image-1":
            msg = f"Streaming not supported for model '{self.model.id}'. Only 'gpt-image-1' supports streaming."
            raise ValueError(msg)

        request_body["stream"] = True

        if "partial_images" not in request_body:
            request_body["partial_images"] = 1

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

        return self.http_client.stream_post(
            f"{config.BASE_URL}{config.STREAM_ENDPOINT}",
            headers=headers,
            json_body=request_body,
        )


__all__ = ["OpenAIImageGenerationClient"]
