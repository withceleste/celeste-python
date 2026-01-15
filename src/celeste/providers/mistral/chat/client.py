"""Mistral Chat API client mixin."""

from collections.abc import AsyncIterator
from typing import Any

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config


class MistralChatClient(APIMixin):
    """Mixin for Mistral Chat API capabilities.

    Provides shared implementation for chat-based capabilities:
    - _make_request() - HTTP POST to /v1/chat/completions
    - _make_stream_request() - SSE streaming to /v1/chat/completions
    - _parse_usage() - Extract usage dict from response
    - _parse_content() - Extract choices from response
    - _parse_finish_reason() - Extract finish reason from response
    - _build_metadata() - Filter content fields

    Usage:
        class MistralTextGenerationClient(MistralChatClient, TextGenerationClient):
            def _parse_content(self, response_data, **parameters):
                choices = super()._parse_content(response_data)
                message = choices[0].get("message", {})
                content = message.get("content") or ""
                return self._transform_output(content, **parameters)
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
        """Make HTTP request to Mistral Chat API."""
        if endpoint is None:
            endpoint = config.MistralChatEndpoint.CREATE_CHAT_COMPLETION

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
        """Make HTTP streaming request to Mistral Chat API."""
        if endpoint is None:
            endpoint = config.MistralChatEndpoint.CREATE_CHAT_COMPLETION

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
        """Map Mistral usage fields to unified names.

        Shared by client and streaming across all capabilities.
        """
        return {
            UsageField.INPUT_TOKENS: usage_data.get("prompt_tokens"),
            UsageField.OUTPUT_TOKENS: usage_data.get("completion_tokens"),
            UsageField.TOTAL_TOKENS: usage_data.get("total_tokens"),
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from response."""
        usage_data = response_data.get("usage", {})
        return MistralChatClient.map_usage_fields(usage_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Return choices from response."""
        choices = response_data.get("choices", [])
        if not choices:
            msg = "No choices in response"
            raise ValueError(msg)
        return choices

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Extract finish reason from choices."""
        choices = response_data.get("choices", [])
        if not choices:
            reason = None
        else:
            reason = choices[0].get("finish_reason")
        return FinishReason(reason=reason)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary, filtering out content fields."""
        content_fields = {"choices"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)


__all__ = ["MistralChatClient"]
