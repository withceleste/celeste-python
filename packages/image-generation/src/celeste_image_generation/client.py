"""Base client for image generation."""

from abc import abstractmethod
from typing import Any, Unpack

import httpx

from celeste.artifacts import ImageArtifact
from celeste.client import Client
from celeste.exceptions import ValidationError
from celeste_image_generation.io import (
    ImageGenerationFinishReason,
    ImageGenerationInput,
    ImageGenerationOutput,
    ImageGenerationUsage,
)
from celeste_image_generation.parameters import ImageGenerationParameters


class ImageGenerationClient(
    Client[ImageGenerationInput, ImageGenerationOutput, ImageGenerationParameters]
):
    """Client for image generation operations."""

    @abstractmethod
    def _init_request(self, inputs: ImageGenerationInput) -> dict[str, Any]:
        """Initialize provider-specific request structure."""

    @abstractmethod
    def _parse_usage(self, response_data: dict[str, Any]) -> ImageGenerationUsage:
        """Parse usage information from provider response."""

    @abstractmethod
    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> ImageArtifact:
        """Parse content from provider response."""

    @abstractmethod
    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> ImageGenerationFinishReason | None:
        """Parse finish reason from provider response."""

    def _create_inputs(
        self, *args: str, **parameters: Unpack[ImageGenerationParameters]
    ) -> ImageGenerationInput:
        """Map positional arguments to Input type."""
        if args:
            return ImageGenerationInput(prompt=args[0])
        prompt: str | None = parameters.get("prompt")
        if prompt is None:
            msg = (
                "prompt is required (either as positional argument or keyword argument)"
            )
            raise ValidationError(msg)
        return ImageGenerationInput(prompt=prompt)

    @classmethod
    def _output_class(cls) -> type[ImageGenerationOutput]:
        """Return the Output class for this client."""
        return ImageGenerationOutput

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        metadata = super()._build_metadata(response_data)
        metadata["raw_response"] = response_data
        return metadata

    @abstractmethod
    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""
