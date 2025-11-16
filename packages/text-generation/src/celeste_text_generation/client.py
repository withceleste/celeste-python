"""Base client for text generation."""

from abc import abstractmethod
from typing import Any, Unpack

import httpx
from pydantic import BaseModel

from celeste.client import Client
from celeste.exceptions import ValidationError
from celeste_text_generation.io import (
    TextGenerationFinishReason,
    TextGenerationInput,
    TextGenerationOutput,
    TextGenerationUsage,
)
from celeste_text_generation.parameters import TextGenerationParameters


class TextGenerationClient(
    Client[TextGenerationInput, TextGenerationOutput, TextGenerationParameters]
):
    """Client for text generation operations."""

    @abstractmethod
    def _init_request(self, inputs: TextGenerationInput) -> dict[str, Any]:
        """Initialize provider-specific request structure."""

    @abstractmethod
    def _parse_usage(self, response_data: dict[str, Any]) -> TextGenerationUsage:
        """Parse usage information from provider response."""

    @abstractmethod
    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[TextGenerationParameters],
    ) -> str | BaseModel:
        """Parse content from provider response."""

    @abstractmethod
    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> TextGenerationFinishReason | None:
        """Parse finish reason from provider response."""

    def _create_inputs(
        self, *args: str, **parameters: Unpack[TextGenerationParameters]
    ) -> TextGenerationInput:
        """Map positional arguments to Input type."""
        if args:
            return TextGenerationInput(prompt=args[0])
        prompt: str | None = parameters.get("prompt")
        if prompt is None:
            msg = (
                "prompt is required (either as positional argument or keyword argument)"
            )
            raise ValidationError(msg)
        return TextGenerationInput(prompt=prompt)

    @classmethod
    def _output_class(cls) -> type[TextGenerationOutput]:
        """Return the Output class for this client."""
        return TextGenerationOutput

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        metadata = super()._build_metadata(response_data)
        metadata["raw_response"] = response_data
        return metadata

    @abstractmethod
    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[TextGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""
