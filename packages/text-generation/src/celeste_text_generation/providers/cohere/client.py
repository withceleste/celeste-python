"""Cohere client implementation for text generation."""

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
from .parameters import COHERE_PARAMETER_MAPPERS
from .streaming import CohereTextGenerationStream


class CohereTextGenerationClient(TextGenerationClient):
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
        meta = response_data.get("meta", {})

        billed_units = meta.get("billed_units", {})
        tokens = meta.get("tokens", {})

        input_tokens = billed_units.get("input_tokens")
        output_tokens = billed_units.get("output_tokens")

        if input_tokens is not None or output_tokens is not None:
            return TextGenerationUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=tokens.get("total_tokens") if tokens else None,
                cached_tokens=meta.get("cached_tokens"),
            )

        return TextGenerationUsage()

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[TextGenerationParameters],
    ) -> str | BaseModel:
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
    ) -> TextGenerationFinishReason | None:
        """Parse finish reason from response."""
        finish_reason_str = response_data.get("finish_reason")
        return (
            TextGenerationFinishReason(reason=finish_reason_str)
            if finish_reason_str
            else None
        )

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        # Filter content field before calling super
        content_fields = {"message"}
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

    def _stream_class(self) -> type[CohereTextGenerationStream]:
        """Return the Stream class for this client."""
        return CohereTextGenerationStream

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


__all__ = ["CohereTextGenerationClient"]
