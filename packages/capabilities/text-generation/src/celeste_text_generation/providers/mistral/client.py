"""Mistral client implementation for text generation."""

from typing import Any, Unpack

from celeste_mistral.chat.client import MistralChatClient

from celeste.parameters import ParameterMapper
from celeste.types import StructuredOutput
from celeste_text_generation.client import TextGenerationClient
from celeste_text_generation.io import (
    TextGenerationFinishReason,
    TextGenerationInput,
    TextGenerationUsage,
)
from celeste_text_generation.parameters import TextGenerationParameters

from .parameters import MISTRAL_PARAMETER_MAPPERS
from .streaming import MistralTextGenerationStream


class MistralTextGenerationClient(MistralChatClient, TextGenerationClient):
    """Mistral client for text generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return MISTRAL_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextGenerationInput) -> dict[str, Any]:
        """Initialize request from Mistral messages array format."""
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
        choices = response_data.get("choices", [])
        if not choices:
            msg = "No choices in response"
            raise ValueError(msg)

        first_choice = choices[0]
        message = first_choice.get("message", {})
        content = message.get("content") or ""

        # Handle magistral thinking models that return list content
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            content = "".join(text_parts)

        return self._transform_output(content, **parameters)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> TextGenerationFinishReason:
        """Parse finish reason from response."""
        choices = response_data.get("choices", [])
        if not choices:
            finish_reason_str = None
        else:
            first_choice = choices[0]
            finish_reason_str = first_choice.get("finish_reason")
        return TextGenerationFinishReason(reason=finish_reason_str)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        # Filter content field before calling super
        content_fields = {"choices"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)

    def _stream_class(self) -> type[MistralTextGenerationStream]:
        """Return the Stream class for this client."""
        return MistralTextGenerationStream


__all__ = ["MistralTextGenerationClient"]
