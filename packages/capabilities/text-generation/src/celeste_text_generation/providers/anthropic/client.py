"""Anthropic client implementation for text generation."""

from typing import Any, Unpack

from celeste_anthropic.messages.client import AnthropicMessagesClient

from celeste.parameters import ParameterMapper
from celeste.types import StructuredOutput
from celeste_text_generation.client import TextGenerationClient
from celeste_text_generation.io import (
    TextGenerationFinishReason,
    TextGenerationInput,
    TextGenerationUsage,
)
from celeste_text_generation.parameters import TextGenerationParameters

from .parameters import ANTHROPIC_PARAMETER_MAPPERS
from .streaming import AnthropicTextGenerationStream


class AnthropicTextGenerationClient(AnthropicMessagesClient, TextGenerationClient):
    """Anthropic client for text generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return ANTHROPIC_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextGenerationInput) -> dict[str, Any]:
        """Initialize request from Anthropic Messages API format."""
        return {"messages": [{"role": "user", "content": inputs.prompt}]}

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
        content = super()._parse_content(response_data)

        text_content = ""
        for content_block in content:
            if content_block.get("type") == "text":
                text_content = content_block.get("text") or ""
                break

        return self._transform_output(text_content, **parameters)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> TextGenerationFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return TextGenerationFinishReason(reason=finish_reason.reason)

    def _stream_class(self) -> type[AnthropicTextGenerationStream]:
        """Return the Stream class for this client."""
        return AnthropicTextGenerationStream


__all__ = ["AnthropicTextGenerationClient"]
