"""Google client implementation for text generation."""

from typing import Any, Unpack

from celeste_google.generate_content.client import GoogleGenerateContentClient

from celeste.parameters import ParameterMapper
from celeste.types import StructuredOutput
from celeste_text_generation.client import TextGenerationClient
from celeste_text_generation.io import (
    TextGenerationFinishReason,
    TextGenerationInput,
    TextGenerationUsage,
)
from celeste_text_generation.parameters import TextGenerationParameters

from .parameters import GOOGLE_PARAMETER_MAPPERS
from .streaming import GoogleTextGenerationStream


class GoogleTextGenerationClient(GoogleGenerateContentClient, TextGenerationClient):
    """Google client for text generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return GOOGLE_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextGenerationInput) -> dict[str, Any]:
        """Initialize request from Google contents array format."""
        return {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": inputs.prompt}],
                }
            ]
        }

    def _parse_usage(self, response_data: dict[str, Any]) -> TextGenerationUsage:
        """Parse usage from response."""
        usage = super()._parse_usage(response_data)
        return TextGenerationUsage(**usage)

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[TextGenerationParameters],
    ) -> StructuredOutput:
        """Parse content from response."""
        candidates = super()._parse_content(response_data)
        parts = candidates[0].get("content", {}).get("parts", [])
        text = parts[0].get("text") if parts else ""
        return self._transform_output(text or "", **parameters)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> TextGenerationFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return TextGenerationFinishReason(reason=finish_reason.reason)

    def _stream_class(self) -> type[GoogleTextGenerationStream]:
        """Return the Stream class for this client."""
        return GoogleTextGenerationStream


__all__ = ["GoogleTextGenerationClient"]
