"""Base client for video generation."""

from abc import abstractmethod
from typing import Any, Unpack

import httpx

from celeste.artifacts import VideoArtifact
from celeste.client import Client
from celeste.exceptions import ValidationError
from celeste_video_generation.io import (
    VideoGenerationInput,
    VideoGenerationOutput,
    VideoGenerationUsage,
)
from celeste_video_generation.parameters import VideoGenerationParameters


class VideoGenerationClient(
    Client[VideoGenerationInput, VideoGenerationOutput, VideoGenerationParameters]
):
    """Client for video generation operations."""

    @abstractmethod
    def _init_request(self, inputs: VideoGenerationInput) -> dict[str, Any]:
        """Initialize provider-specific request structure."""

    @abstractmethod
    def _parse_usage(self, response_data: dict[str, Any]) -> VideoGenerationUsage:
        """Parse usage information from provider response."""

    @abstractmethod
    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[VideoGenerationParameters],
    ) -> VideoArtifact:
        """Parse content from provider response."""

    def _create_inputs(
        self, *args: str, **parameters: Unpack[VideoGenerationParameters]
    ) -> VideoGenerationInput:
        """Map positional arguments to Input type."""
        if args:
            return VideoGenerationInput(prompt=args[0])
        prompt: str | None = parameters.get("prompt")
        if prompt is None:
            msg = (
                "prompt is required (either as positional argument or keyword argument)"
            )
            raise ValidationError(msg)
        return VideoGenerationInput(prompt=prompt)

    @classmethod
    def _output_class(cls) -> type[VideoGenerationOutput]:
        """Return the Output class for this client."""
        return VideoGenerationOutput

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        metadata = super()._build_metadata(response_data)
        metadata["raw_response"] = response_data
        return metadata

    @abstractmethod
    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[VideoGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""
