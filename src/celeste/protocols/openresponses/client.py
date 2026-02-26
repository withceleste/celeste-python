"""OpenResponses protocol client."""

from collections.abc import AsyncIterator
from typing import Any, ClassVar

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.io import FinishReason

from . import config


class OpenResponsesClient(APIMixin):
    """OpenResponses protocol client.

    Provides shared implementation for all providers using the Responses API:
    - _build_url() - Build URL with provider base URL (override for Vertex AI)
    - _build_request() - Add model ID and streaming flag
    - _make_request() - HTTP POST to /v1/responses
    - _make_stream_request() - HTTP streaming to /v1/responses
    - map_usage_fields() - Map usage fields to unified names
    - _parse_usage() - Extract usage dict from response
    - _parse_content() - Extract output array from response
    - _parse_finish_reason() - Extract finish reason from response
    - _content_fields: ClassVar - Content field names to exclude from metadata

    Providers override ClassVars and hook methods:
    - _default_base_url: ClassVar[str] - Provider's API base URL
    - _default_endpoint: ClassVar[str] - Default endpoint path (override for non-standard paths)
    - _build_url() - Override for Vertex AI URL routing
    - map_usage_fields() - Override to add provider-specific usage fields
    - _build_request() - Override to add provider-specific request fields

    Usage:
        class OpenAIResponsesClient(OpenResponsesClient):
            _default_base_url: ClassVar[str] = config.BASE_URL
    """

    _default_base_url: ClassVar[str] = config.DEFAULT_BASE_URL
    _default_endpoint: ClassVar[str] = config.OpenResponsesEndpoint.CREATE_RESPONSE
    _content_fields: ClassVar[set[str]] = {"output"}

    def _build_url(self, endpoint: str, streaming: bool = False) -> str:
        """Build full URL for request.

        Override for Vertex AI support:
            def _build_url(self, endpoint: str, streaming: bool = False) -> str:
                if isinstance(self.auth, GoogleADC):
                    return self.auth.build_url(self._get_vertex_endpoint(endpoint, streaming))
                return super()._build_url(endpoint, streaming)
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
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to Responses API endpoint."""
        if endpoint is None:
            endpoint = self._default_endpoint

        headers = self._json_headers(extra_headers)

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
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Make streaming request to Responses API endpoint."""
        if endpoint is None:
            endpoint = self._default_endpoint

        headers = self._json_headers(extra_headers)

        return self.http_client.stream_post(
            self._build_url(endpoint, streaming=True),
            headers=headers,
            json_body=request_body,
        )

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map Responses usage fields to unified names."""
        input_details = usage_data.get("input_tokens_details", {})
        output_details = usage_data.get("output_tokens_details", {})
        return {
            UsageField.INPUT_TOKENS: usage_data.get("input_tokens"),
            UsageField.OUTPUT_TOKENS: usage_data.get("output_tokens"),
            UsageField.TOTAL_TOKENS: usage_data.get("total_tokens"),
            UsageField.CACHED_TOKENS: input_details.get("cached_tokens"),
            UsageField.REASONING_TOKENS: output_details.get("reasoning_tokens"),
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from Responses API response."""
        usage_data = response_data.get("usage", {})
        return self.map_usage_fields(usage_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse output array from Responses API."""
        output = response_data.get("output", [])
        if not output:
            msg = "No output in response"
            raise ValueError(msg)
        return output

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Extract finish reason from Responses API response."""
        status = response_data.get("status")
        if status == "completed":
            output_items = response_data.get("output", [])
            for item in output_items:
                if item.get("type") == "message" and item.get("status") == "completed":
                    return FinishReason(reason="completed")
        return FinishReason(reason=None)


__all__ = ["OpenResponsesClient"]
