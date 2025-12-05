"""Base client for music generation."""

from abc import abstractmethod
from typing import Any, Unpack

import httpx

from celeste.artifacts import AudioArtifact
from celeste.client import Client
from celeste.exceptions import ValidationError
from celeste_music_generation.io import (
    MusicGenerationFinishReason,
    MusicGenerationInput,
    MusicGenerationOutput,
    MusicGenerationUsage,
)
from celeste_music_generation.parameters import MusicGenerationParameters


class MusicGenerationClient(
    Client[MusicGenerationInput, MusicGenerationOutput, MusicGenerationParameters]
):
    """Client for music generation operations."""

    @abstractmethod
    def _init_request(self, inputs: MusicGenerationInput) -> dict[str, Any]:
        """Initialize provider-specific request structure."""

    @abstractmethod
    def _parse_usage(self, response_data: dict[str, Any]) -> MusicGenerationUsage:
        """Parse usage information from provider response."""

    @abstractmethod
    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[MusicGenerationParameters],
    ) -> AudioArtifact:
        """Parse content from provider response."""

    @abstractmethod
    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> MusicGenerationFinishReason | None:
        """Parse finish reason from provider response."""

    def _create_inputs(
        self,
        *args: str,
        prompt: str | None = None,
        **parameters: Unpack[MusicGenerationParameters],
    ) -> MusicGenerationInput:
        """Map positional arguments to Input type."""
        if args:
            return MusicGenerationInput(prompt=args[0])
        if prompt is None:
            msg = (
                "prompt is required (either as positional argument or keyword argument)"
            )
            raise ValidationError(msg)
        return MusicGenerationInput(prompt=prompt)

    @classmethod
    def _output_class(cls) -> type[MusicGenerationOutput]:
        """Return the Output class for this client."""
        return MusicGenerationOutput

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        metadata = super()._build_metadata(response_data)
        metadata["raw_response"] = response_data
        return metadata

    @abstractmethod
    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[MusicGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""


__all__ = ["MusicGenerationClient"]
