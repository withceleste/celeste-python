"""OpenAI client implementation for text generation."""

from typing import Any, Unpack

from celeste_openai.responses.client import OpenAIResponsesClient

from celeste.parameters import ParameterMapper
from celeste.types import StructuredOutput
from celeste_text_generation.client import TextGenerationClient
from celeste_text_generation.io import (
    TextGenerationFinishReason,
    TextGenerationInput,
    TextGenerationUsage,
)
from celeste_text_generation.parameters import TextGenerationParameters

from .parameters import OPENAI_PARAMETER_MAPPERS
from .streaming import OpenAITextGenerationStream


class OpenAITextGenerationClient(OpenAIResponsesClient, TextGenerationClient):
    """OpenAI client for text generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return OPENAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextGenerationInput) -> dict[str, Any]:
        """Initialize request from OpenAI Responses API format."""
        return {"input": inputs.prompt}

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
        output = super()._parse_content(response_data)  # Raw output array
        # Find message item and extract text
        for item in output:
            if item.get("type") == "message":
                for part in item.get("content", []):
                    if part.get("type") == "output_text":
                        text = part.get("text") or ""
                        return self._transform_output(text, **parameters)
        return ""

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> TextGenerationFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return TextGenerationFinishReason(reason=finish_reason.reason)

    def _stream_class(self) -> type[OpenAITextGenerationStream]:
        """Return the Stream class for this client."""
        return OpenAITextGenerationStream


__all__ = ["OpenAITextGenerationClient"]
