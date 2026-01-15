"""Cohere Chat API client mixin."""

from collections.abc import AsyncIterator
from typing import Any

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config


class CohereChatClient(APIMixin):
    """Mixin for Cohere Chat API capabilities.

    Provides shared implementation for all capabilities using the Chat API:
    - _make_request() - HTTP POST to /v2/chat
    - _make_stream_request() - HTTP streaming to /v2/chat
    - _parse_usage() - Extract usage dict from response
    - _parse_content() - Extract content array from response message
    - _parse_finish_reason() - Extract finish reason from response
    - _build_metadata() - Filter content fields

    Usage:
        class CohereTextGenerationClient(CohereChatClient, TextGenerationClient):
            def _parse_content(self, response_data, **parameters):
                content_array = super()._parse_content(response_data)
                text = content_array[0].get("text") or ""
                return self._transform_output(text, **parameters)
    """

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
        """Make HTTP request to Cohere Chat API endpoint."""
        if endpoint is None:
            endpoint = config.CohereChatEndpoint.CREATE_CHAT

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

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
        """Make streaming request to Cohere Chat API endpoint."""
        if endpoint is None:
            endpoint = config.CohereChatEndpoint.CREATE_CHAT

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        return self.http_client.stream_post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map Cohere usage fields to unified names.

        Shared by client and streaming across all capabilities.
        """
        billed_units = usage_data.get("billed_units", {})
        tokens = usage_data.get("tokens", {})
        return {
            UsageField.INPUT_TOKENS: billed_units.get("input_tokens"),
            UsageField.OUTPUT_TOKENS: billed_units.get("output_tokens"),
            UsageField.TOTAL_TOKENS: tokens.get("total_tokens") if tokens else None,
            UsageField.CACHED_TOKENS: usage_data.get("cached_tokens"),
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from Chat API response."""
        usage_data = response_data.get("usage", {})
        return CohereChatClient.map_usage_fields(usage_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse content array from Chat API response message.

        Returns raw content array that capability clients extract from.
        """
        message = response_data.get("message", {})
        content_array = message.get("content", [])
        if not content_array:
            msg = "No content in response message"
            raise ValueError(msg)
        return content_array

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Extract finish reason from Chat API response."""
        reason = response_data.get("finish_reason")
        return FinishReason(reason=reason)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary, filtering out content fields."""
        content_fields = {"message"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)


__all__ = ["CohereChatClient"]
