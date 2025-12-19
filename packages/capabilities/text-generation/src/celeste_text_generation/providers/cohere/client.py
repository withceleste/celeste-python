"""Cohere client implementation for text generation."""

from typing import Any, Unpack

from celeste_cohere.chat.client import CohereChatClient

from celeste.parameters import ParameterMapper
from celeste.types import StructuredOutput
from celeste_text_generation.client import TextGenerationClient
from celeste_text_generation.io import (
    TextGenerationFinishReason,
    TextGenerationInput,
    TextGenerationUsage,
)
from celeste_text_generation.parameters import TextGenerationParameters

from .parameters import COHERE_PARAMETER_MAPPERS
from .streaming import CohereTextGenerationStream


class CohereTextGenerationClient(CohereChatClient, TextGenerationClient):
    """Cohere client for text generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return COHERE_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextGenerationInput) -> dict[str, Any]:
        """Initialize request from Cohere v2 Chat API messages array format."""
        messages = [
            {
                "role": "user",
                "content": inputs.prompt,
            }
        ]

        return {"messages": messages}

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
        message = response_data.get("message", {})
        content_array = message.get("content", [])
        if not content_array:
            msg = "No content in response message"
            raise ValueError(msg)

        first_content = content_array[0]
        text = first_content.get("text") or ""

        return self._transform_output(text, **parameters)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> TextGenerationFinishReason:
        """Parse finish reason from response."""
        finish_reason_str = response_data.get("finish_reason")
        return TextGenerationFinishReason(reason=finish_reason_str)

    def _stream_class(self) -> type[CohereTextGenerationStream]:
        """Return the Stream class for this client."""
        return CohereTextGenerationStream


__all__ = ["CohereTextGenerationClient"]
