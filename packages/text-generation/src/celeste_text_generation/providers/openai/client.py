"""OpenAI client implementation for text generation."""

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
from .parameters import OPENAI_PARAMETER_MAPPERS
from .streaming import OpenAITextGenerationStream


class OpenAITextGenerationClient(TextGenerationClient):
    """OpenAI client for text generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return OPENAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextGenerationInput) -> dict[str, Any]:
        """Initialize request from OpenAI Responses API format."""
        return {"input": inputs.prompt}

    def _parse_usage(self, response_data: dict[str, Any]) -> TextGenerationUsage:
        """Parse usage from response."""
        usage_data = response_data.get("usage", {})
        input_tokens_details = usage_data.get("input_tokens_details", {})
        output_tokens_details = usage_data.get("output_tokens_details", {})

        return TextGenerationUsage(
            input_tokens=usage_data.get("input_tokens"),
            output_tokens=usage_data.get("output_tokens"),
            total_tokens=usage_data.get("total_tokens"),
            cached_tokens=input_tokens_details.get("cached_tokens"),
            reasoning_tokens=output_tokens_details.get("reasoning_tokens"),
            billed_tokens=None,
        )

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[TextGenerationParameters],
    ) -> str | BaseModel:
        """Parse content from response."""
        output_items = response_data.get("output", [])
        if not output_items:
            msg = "No output items in response"
            raise ValueError(msg)

        message_item = None
        for item in output_items:
            if item.get("type") == "message":
                message_item = item
                break

        if not message_item:
            msg = "No message item found in output array"
            raise ValueError(msg)

        content_parts = message_item.get("content", [])
        if not content_parts:
            msg = "No content parts in message item"
            raise ValueError(msg)

        text_content = ""
        for content_part in content_parts:
            if content_part.get("type") == "output_text":
                text_content = content_part.get("text") or ""
                break

        return self._transform_output(text_content, **parameters)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> TextGenerationFinishReason | None:
        """Parse finish reason from response."""
        status = response_data.get("status")
        if status != "completed":
            return None

        output_items = response_data.get("output", [])
        for item in output_items:
            if item.get("type") == "message":
                item_status = item.get("status")
                if item_status == "completed":
                    return TextGenerationFinishReason(reason="completed")

        return None

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        # Filter content field before calling super
        content_fields = {"output"}
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

    def _stream_class(self) -> type[OpenAITextGenerationStream]:
        """Return the Stream class for this client."""
        return OpenAITextGenerationStream

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


__all__ = ["OpenAITextGenerationClient"]
