"""Anthropic client implementation for text generation."""

from collections.abc import AsyncIterator
from typing import Any, Unpack

import httpx
from pydantic import BaseModel

from celeste.mime_types import ApplicationMimeType
from celeste.parameters import ParameterMapper
from celeste_text_generation.client import TextGenerationClient
from celeste_text_generation.io import (
    TextGenerationFinishReason,
    TextGenerationInput,
    TextGenerationUsage,
)
from celeste_text_generation.parameters import (
    TextGenerationParameter,
    TextGenerationParameters,
)

from . import config
from .parameters import ANTHROPIC_PARAMETER_MAPPERS
from .streaming import AnthropicTextGenerationStream


class AnthropicTextGenerationClient(TextGenerationClient):
    """Anthropic client for text generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return ANTHROPIC_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextGenerationInput) -> dict[str, Any]:
        """Initialize request from Anthropic Messages API format."""
        return {"messages": [{"role": "user", "content": inputs.prompt}]}

    def _parse_usage(self, response_data: dict[str, Any]) -> TextGenerationUsage:
        """Parse usage from response."""
        usage_data = response_data.get("usage", {})
        input_tokens = usage_data.get("input_tokens")
        output_tokens = usage_data.get("output_tokens")

        total_tokens = None
        if input_tokens is not None and output_tokens is not None:
            total_tokens = input_tokens + output_tokens

        return TextGenerationUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            billed_tokens=None,
            cached_tokens=None,
            reasoning_tokens=None,
        )

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[TextGenerationParameters],
    ) -> str | BaseModel:
        """Parse content from response."""
        content = response_data.get("content", [])
        if not content:
            msg = "No content blocks in response"
            raise ValueError(msg)

        text_content = ""
        for content_block in content:
            if content_block.get("type") == "text":
                text_content = content_block.get("text") or ""
                break

        return self._transform_output(text_content, **parameters)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> TextGenerationFinishReason | None:
        """Parse finish reason from response."""
        stop_reason = response_data.get("stop_reason")
        if stop_reason is None:
            return None

        return TextGenerationFinishReason(reason=stop_reason)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        # Filter content field before calling super
        content_fields = {"content"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[TextGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""
        request_body["model"] = self.model.id
        request_body["max_tokens"] = parameters.get("max_tokens") or 1024

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            config.ANTHROPIC_VERSION_HEADER: config.ANTHROPIC_VERSION,
            "Content-Type": ApplicationMimeType.JSON,
        }

        if parameters.get(TextGenerationParameter.OUTPUT_SCHEMA) is not None:
            headers[config.ANTHROPIC_BETA_HEADER] = config.STRUCTURED_OUTPUTS_BETA

        return await self.http_client.post(
            f"{config.BASE_URL}{config.ENDPOINT}",
            headers=headers,
            json_body=request_body,
        )

    def _stream_class(self) -> type[AnthropicTextGenerationStream]:
        """Return the Stream class for this client."""
        return AnthropicTextGenerationStream

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[TextGenerationParameters],
    ) -> AsyncIterator[dict[str, Any]]:
        """Make HTTP streaming request and return async iterator of events."""
        request_body["model"] = self.model.id
        request_body["max_tokens"] = parameters.get("max_tokens") or 1024
        request_body["stream"] = True

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            config.ANTHROPIC_VERSION_HEADER: config.ANTHROPIC_VERSION,
            "Content-Type": ApplicationMimeType.JSON,
        }

        if parameters.get(TextGenerationParameter.OUTPUT_SCHEMA) is not None:
            headers[config.ANTHROPIC_BETA_HEADER] = config.STRUCTURED_OUTPUTS_BETA

        return self.http_client.stream_post(
            f"{config.BASE_URL}{config.STREAM_ENDPOINT}",
            headers=headers,
            json_body=request_body,
        )


__all__ = ["AnthropicTextGenerationClient"]
