"""Anthropic Messages API client mixin."""

from collections.abc import AsyncIterator
from typing import Any

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config


class AnthropicMessagesClient(APIMixin):
    """Mixin for Anthropic Messages API capabilities.

    Provides shared implementation for all capabilities using the Messages API:
    - _make_request() - HTTP POST to /v1/messages
    - _make_stream_request() - HTTP streaming to /v1/messages
    - _parse_usage() - Extract usage dict from response
    - _parse_content() - Extract content array from response
    - _parse_finish_reason() - Extract finish reason from response
    - _build_metadata() - Filter content fields

    Usage:
        class AnthropicTextGenerationClient(AnthropicMessagesClient, TextGenerationClient):
            def _parse_content(self, response_data, **parameters):
                content = super()._parse_content(response_data)  # Raw content array
                for block in content:
                    if block.get("type") == "text":
                        return self._transform_output(block.get("text") or "", **parameters)
                return ""
    """

    def _build_headers(self, request_body: dict[str, Any]) -> dict[str, str]:
        """Build headers with beta features extracted from request."""
        beta_features: list[str] = request_body.pop("_beta_features", [])

        headers: dict[str, str] = {
            **self.auth.get_headers(),
            config.HEADER_ANTHROPIC_VERSION: config.ANTHROPIC_VERSION,
            "Content-Type": ApplicationMimeType.JSON,
        }

        if beta_features:
            beta_values = [
                getattr(config, f"BETA_{f.upper().replace('-', '_')}")
                for f in beta_features
            ]
            headers[config.HEADER_ANTHROPIC_BETA] = ",".join(beta_values)

        return headers

    def _build_request(
        self,
        inputs: Any,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Build request with model ID and streaming flag."""
        request_body = super()._build_request(
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )
        request_body["model"] = self.model.id
        if streaming:
            request_body["stream"] = True
        return request_body

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to Anthropic Messages API endpoint."""
        # Apply max_tokens default if not set (Anthropic requires it)
        if "max_tokens" not in request_body:
            request_body["max_tokens"] = config.DEFAULT_MAX_TOKENS

        headers = self._build_headers(request_body)

        if endpoint is None:
            endpoint = config.AnthropicMessagesEndpoint.CREATE_MESSAGE

        response = await self.http_client.post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )
        self._handle_error_response(response)
        data: dict[str, Any] = response.json()
        return data

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Make streaming request to Anthropic Messages API endpoint."""
        # Apply max_tokens default if not set (Anthropic requires it)
        if "max_tokens" not in request_body:
            request_body["max_tokens"] = config.DEFAULT_MAX_TOKENS

        headers = self._build_headers(request_body)

        if endpoint is None:
            endpoint = config.AnthropicMessagesEndpoint.CREATE_MESSAGE

        return self.http_client.stream_post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map Anthropic usage fields to unified names.

        Shared by client and streaming across all capabilities.
        """
        input_tokens = usage_data.get("input_tokens")
        output_tokens = usage_data.get("output_tokens")
        cached_tokens = usage_data.get("cache_read_input_tokens")
        total_tokens = (
            (input_tokens + output_tokens)
            if (input_tokens is not None and output_tokens is not None)
            else None
        )
        return {
            UsageField.INPUT_TOKENS: input_tokens,
            UsageField.OUTPUT_TOKENS: output_tokens,
            UsageField.TOTAL_TOKENS: total_tokens,
            UsageField.CACHED_TOKENS: cached_tokens,
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from Messages API response."""
        usage_data = response_data.get("usage", {})
        return AnthropicMessagesClient.map_usage_fields(usage_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse content array from Messages API.

        Returns raw content array that capability clients extract from.
        """
        content = response_data.get("content", [])
        if not content:
            msg = "No content in response"
            raise ValueError(msg)
        return content

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Extract finish reason from Messages API response.

        Returns FinishReason that capability clients wrap in their specific type.
        """
        stop_reason = response_data.get("stop_reason")
        return FinishReason(reason=stop_reason)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary, filtering out content fields."""
        content_fields = {"content"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)


__all__ = ["AnthropicMessagesClient"]
