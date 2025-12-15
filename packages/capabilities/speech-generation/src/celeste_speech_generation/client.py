"""Base client for speech generation."""

from abc import abstractmethod
from typing import Any, Unpack

import httpx

from celeste.artifacts import AudioArtifact
from celeste.client import Client
from celeste.exceptions import ValidationError
from celeste_speech_generation.io import (
    SpeechGenerationInput,
    SpeechGenerationOutput,
    SpeechGenerationUsage,
)
from celeste_speech_generation.parameters import SpeechGenerationParameters


class SpeechGenerationClient(
    Client[SpeechGenerationInput, SpeechGenerationOutput, SpeechGenerationParameters]
):
    """Client for speech generation operations."""

    @abstractmethod
    def _init_request(self, inputs: SpeechGenerationInput) -> dict[str, Any]:
        """Initialize provider-specific request structure."""

    @abstractmethod
    def _parse_usage(self, response_data: dict[str, Any]) -> SpeechGenerationUsage:
        """Parse usage information from provider response."""

    @abstractmethod
    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> AudioArtifact:
        """Parse content from provider response."""

    def _create_inputs(
        self, *args: str, **parameters: Unpack[SpeechGenerationParameters]
    ) -> SpeechGenerationInput:
        """Map positional arguments to Input type."""
        if args:
            return SpeechGenerationInput(text=args[0])
        text: str | None = parameters.get("text")
        if text is None:
            msg = "text is required (either as positional argument or keyword argument)"
            raise ValidationError(msg)
        return SpeechGenerationInput(text=text)

    @classmethod
    def _output_class(cls) -> type[SpeechGenerationOutput]:
        """Return the Output class for this client."""
        return SpeechGenerationOutput

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        metadata = super()._build_metadata(response_data)
        metadata["raw_response"] = response_data
        return metadata

    @abstractmethod
    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[SpeechGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""
