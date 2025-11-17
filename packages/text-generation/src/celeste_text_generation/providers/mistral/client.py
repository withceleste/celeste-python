"""Mistral client implementation for text generation."""

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
from celeste_text_generation.parameters import TextGenerationParameters

from . import config
from .parameters import MISTRAL_PARAMETER_MAPPERS
from .streaming import MistralTextGenerationStream


class MistralTextGenerationClient(TextGenerationClient):
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
        usage_dict = response_data.get("usage", {})

        return TextGenerationUsage(
            input_tokens=usage_dict.get("prompt_tokens"),
            output_tokens=usage_dict.get("completion_tokens"),
            total_tokens=usage_dict.get("total_tokens"),
        )

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[TextGenerationParameters],
    ) -> str | BaseModel:
        """Parse content from response."""
        choices = response_data.get("choices", [])
        if not choices:
            msg = "No choices in response"
            raise ValueError(msg)

        first_choice = choices[0]
        message = first_choice.get("message", {})
        content = message.get("content") or ""

        return self._transform_output(content, **parameters)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> TextGenerationFinishReason | None:
        """Parse finish reason from response."""
        choices = response_data.get("choices", [])
        if not choices:
            return None

        first_choice = choices[0]
        finish_reason_str = first_choice.get("finish_reason")
        return (
            TextGenerationFinishReason(reason=finish_reason_str)
            if finish_reason_str
            else None
        )

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        # Filter content field before calling super
        content_fields = {"choices"}
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

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

        return await self.http_client.post(
            f"{config.BASE_URL}{config.ENDPOINT}",
            headers=headers,
            json_body=request_body,
        )

    def _stream_class(self) -> type[MistralTextGenerationStream]:
        """Return the Stream class for this client."""
        return MistralTextGenerationStream

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[TextGenerationParameters],
    ) -> AsyncIterator[dict[str, Any]]:
        """Make HTTP streaming request and return async iterator of events."""
        request_body["model"] = self.model.id
        request_body["stream"] = True

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

        return self.http_client.stream_post(
            f"{config.BASE_URL}{config.STREAM_ENDPOINT}",
            headers=headers,
            json_body=request_body,
        )


__all__ = ["MistralTextGenerationClient"]
