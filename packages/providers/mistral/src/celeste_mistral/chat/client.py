"""Mistral Chat API client with shared implementation."""

from collections.abc import AsyncIterator
from typing import Any

import httpx

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

    Capability clients extend parsing methods via super() to wrap/transform results.

    Usage:
        class MistralTextGenerationClient(MistralChatClient, TextGenerationClient):
            def _parse_content(self, response_data, **parameters):
                choices = response_data.get("choices", [])
                text = choices[0]["message"]["content"]
                return self._transform_output(text, **parameters)
    """

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Any,
    ) -> httpx.Response:
        """Make HTTP request to Mistral Chat API."""
        request_body["model"] = self.model.id

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        return await self.http_client.post(
            f"{config.BASE_URL}{config.MistralChatEndpoint.CREATE_CHAT_COMPLETION}",
            headers=headers,
            json_body=request_body,
        )

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Make HTTP streaming request to Mistral Chat API."""
        request_body["model"] = self.model.id
        request_body["stream"] = True

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        return self.http_client.stream_post(
            f"{config.BASE_URL}{config.MistralChatEndpoint.CREATE_CHAT_COMPLETION}",
            headers=headers,
            json_body=request_body,
        )

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | None]:
        """Map Mistral usage fields to unified names.

        Shared by client and streaming across all capabilities.
        """
        return {
            UsageField.INPUT_TOKENS: usage_data.get("prompt_tokens"),
            UsageField.OUTPUT_TOKENS: usage_data.get("completion_tokens"),
            UsageField.TOTAL_TOKENS: usage_data.get("total_tokens"),
        }

    def _parse_usage(self, response_data: dict[str, Any]) -> dict[str, int | None]:
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
