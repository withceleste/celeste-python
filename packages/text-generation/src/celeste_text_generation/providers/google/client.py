"""Google client implementation for text generation."""

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
from .parameters import GOOGLE_PARAMETER_MAPPERS
from .streaming import GoogleTextGenerationStream


class GoogleTextGenerationClient(TextGenerationClient):
    """Google client for text generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return GOOGLE_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextGenerationInput) -> dict[str, Any]:
        """Initialize request from Google contents array format."""
        contents = [
            {
                "role": "user",
                "parts": [{"text": inputs.prompt}],
            }
        ]

        return {"contents": contents}

    def _parse_usage(self, response_data: dict[str, Any]) -> TextGenerationUsage:
        """Parse usage from response."""
        usage_metadata = response_data.get("usageMetadata", {})

        return TextGenerationUsage(
            input_tokens=usage_metadata.get("promptTokenCount"),
            output_tokens=usage_metadata.get("candidatesTokenCount"),
            total_tokens=usage_metadata.get("totalTokenCount"),
            reasoning_tokens=usage_metadata.get("thoughtsTokenCount"),
            billed_tokens=None,
            cached_tokens=None,
        )

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[TextGenerationParameters],
    ) -> str | BaseModel:
        """Parse content from response."""
        candidates = response_data.get("candidates", [])
        if not candidates:
            msg = "No candidates in response"
            raise ValueError(msg)

        candidate = candidates[0]
        content = candidate.get("content", {})
        parts = content.get("parts", [])

        if not parts:
            msg = "No parts in candidate content"
            raise ValueError(msg)

        text_part = parts[0]
        text = text_part.get("text") or ""

        return self._transform_output(text, **parameters)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> TextGenerationFinishReason | None:
        """Parse finish reason from response."""
        candidates = response_data.get("candidates", [])
        if not candidates:
            return None

        candidate = candidates[0]
        finish_reason_str = candidate.get("finishReason")

        if not finish_reason_str:
            return None

        return TextGenerationFinishReason(reason=finish_reason_str)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        # Filter content field before calling super
        content_fields = {"candidates"}
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
        endpoint = config.ENDPOINT.format(model_id=self.model.id)

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

        return await self.http_client.post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )

    def _stream_class(self) -> type[GoogleTextGenerationStream]:
        """Return the Stream class for this client."""
        return GoogleTextGenerationStream

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[TextGenerationParameters],
    ) -> AsyncIterator[dict[str, Any]]:
        """Make HTTP streaming request and return async iterator of events."""
        stream_endpoint = config.STREAM_ENDPOINT.format(model_id=self.model.id)

        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

        return self.http_client.stream_post(
            f"{config.BASE_URL}{stream_endpoint}",
            headers=headers,
            json_body=request_body,
        )


__all__ = ["GoogleTextGenerationClient"]
