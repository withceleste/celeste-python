"""Ollama Generate API client mixin."""

import json
from collections.abc import AsyncIterator
from typing import Any, ClassVar

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.io import FinishReason

from . import config


class OllamaGenerateClient(APIMixin):
    """Mixin for Ollama Generate API (/api/generate).

    Provides shared HTTP implementation for Ollama's native API:
    - _make_request() - HTTP POST to /api/generate
    - _make_stream_request() - NDJSON streaming
    - _parse_usage() - Extract usage dict from response
    - _parse_content() - Extract image from response
    - _parse_finish_reason() - Check done field
    - _content_fields: ClassVar - Content field names to exclude from metadata
    """

    _content_fields: ClassVar[set[str]] = {"image", "response"}

    def _build_request(
        self,
        inputs: Any,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Build request with model ID and stream flag."""
        request_body = super()._build_request(
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )
        request_body["model"] = self.model.id
        # Ollama defaults to streaming; explicitly disable for non-streaming
        request_body["stream"] = streaming
        return request_body

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        base_url: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to Ollama Generate API."""
        if endpoint is None:
            endpoint = config.OllamaGenerateEndpoint.GENERATE
        if base_url is None:
            base_url = config.DEFAULT_BASE_URL

        headers = self._json_headers(extra_headers)

        response = await self.http_client.post(
            f"{base_url}{endpoint}",
            headers=headers,
            json_body=request_body,
        )
        self._handle_error_response(response)
        # NDJSON: Ollama returns progress lines, final line has done=true + image
        return json.loads(response.text.strip().splitlines()[-1])

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        base_url: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Make NDJSON streaming request to Ollama Generate API."""
        if endpoint is None:
            endpoint = config.OllamaGenerateEndpoint.GENERATE
        if base_url is None:
            base_url = config.DEFAULT_BASE_URL

        headers = self._json_headers(extra_headers)

        return self.http_client.stream_post_ndjson(
            f"{base_url}{endpoint}",
            headers=headers,
            json_body=request_body,
        )

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map Ollama Generate usage fields to unified names."""
        input_tokens = usage_data.get("prompt_eval_count")
        output_tokens = usage_data.get("eval_count")
        total_tokens = usage_data.get("total_eval_count")
        if (
            total_tokens is None
            and input_tokens is not None
            and output_tokens is not None
        ):
            total_tokens = input_tokens + output_tokens
        return {
            UsageField.INPUT_TOKENS: input_tokens,
            UsageField.OUTPUT_TOKENS: output_tokens,
            UsageField.TOTAL_TOKENS: total_tokens,
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from Ollama Generate API response.

        Ollama image generation doesn't return token usage.
        """
        usage_data = response_data.get("usage", response_data)
        return OllamaGenerateClient.map_usage_fields(usage_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse image content from Ollama Generate API response."""
        image = response_data.get("image")
        if not image:
            msg = "No image in response"
            raise ValueError(msg)
        return image

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Extract finish reason from Ollama Generate API response."""
        done = response_data.get("done", False)
        return FinishReason(reason="completed" if done else None)


__all__ = ["OllamaGenerateClient"]
