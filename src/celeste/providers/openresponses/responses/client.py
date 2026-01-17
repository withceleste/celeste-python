"""OpenResponses API client mixin."""

from collections.abc import AsyncIterator
from typing import Any

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config


class OpenResponsesClient(APIMixin):
    """Mixin for OpenResponses API.

    Provides shared implementation for all capabilities using the Responses API:
    - _make_request() - HTTP POST to /v1/responses
    - _make_stream_request() - HTTP streaming to /v1/responses
    - _parse_usage() - Extract usage dict from response
    - _parse_content() - Extract output array from response
    - _parse_finish_reason() - Extract finish reason from response
    - _build_metadata() - Filter content fields
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
        base_url: str | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to OpenResponses API endpoint."""
        if endpoint is None:
            endpoint = config.OpenResponsesEndpoint.CREATE_RESPONSE
        if base_url is None:
            base_url = config.DEFAULT_BASE_URL

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        response = await self.http_client.post(
            f"{base_url}{endpoint}",
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
        base_url: str | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Make streaming request to OpenResponses API endpoint."""
        if endpoint is None:
            endpoint = config.OpenResponsesEndpoint.CREATE_RESPONSE
        if base_url is None:
            base_url = config.DEFAULT_BASE_URL

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        return self.http_client.stream_post(
            f"{base_url}{endpoint}",
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
        return OpenResponsesClient.map_usage_fields(usage_data)

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

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary, filtering out content fields."""
        content_fields = {"output"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)


__all__ = ["OpenResponsesClient"]
