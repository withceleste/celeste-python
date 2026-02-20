"""Chat Completions protocol client."""

from collections.abc import AsyncIterator
from typing import Any, ClassVar

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config


class ChatCompletionsClient(APIMixin):
    """Chat Completions protocol client.

    Provides shared implementation for all providers using the Chat Completions API:
    - _build_url() - Build URL with provider base URL (override for Vertex AI)
    - _build_request() - Add model ID and streaming flag
    - _make_request() - HTTP POST to /v1/chat/completions
    - _make_stream_request() - HTTP streaming to /v1/chat/completions
    - map_usage_fields() - Map usage fields to unified names
    - _parse_usage() - Extract usage dict from response
    - _parse_content() - Extract choices array from response
    - _parse_finish_reason() - Extract finish reason from response
    - _build_metadata() - Filter content fields

    Providers override ClassVars and hook methods:
    - _default_base_url - Provider's API base URL
    - _default_chat_endpoint - Default endpoint path (override for non-standard paths)
    - _build_url() - Override for Vertex AI URL routing
    - map_usage_fields() - Override to add provider-specific usage fields
    - _build_request() - Override to add provider-specific request fields
    """

    _default_base_url: ClassVar[str] = config.DEFAULT_BASE_URL
    _default_chat_endpoint: ClassVar[str] = config.ChatCompletionsEndpoint.CREATE_CHAT

    def _build_url(self, endpoint: str, streaming: bool = False) -> str:
        """Build full URL for request.

        Override for Vertex AI support.
        """
        return f"{self._default_base_url}{endpoint}"

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
        """Make HTTP request to Chat Completions API endpoint."""
        if endpoint is None:
            endpoint = self._default_chat_endpoint

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        response = await self.http_client.post(
            self._build_url(endpoint),
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
        """Make streaming request to Chat Completions API endpoint."""
        if endpoint is None:
            endpoint = self._default_chat_endpoint

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        return self.http_client.stream_post(
            self._build_url(endpoint, streaming=True),
            headers=headers,
            json_body=request_body,
        )

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map Chat Completions usage fields to unified names.

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
        """Extract usage data from Chat Completions API response."""
        usage_data = response_data.get("usage", {})
        return ChatCompletionsClient.map_usage_fields(usage_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse choices array from Chat Completions API response.

        Returns raw choices array that modality clients extract from.
        """
        choices = response_data.get("choices", [])
        if not choices:
            msg = "No choices in response"
            raise ValueError(msg)
        return choices

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Extract finish reason from Chat Completions API response."""
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


__all__ = ["ChatCompletionsClient"]
