"""Google Interactions API client mixin."""

from collections.abc import AsyncIterator
from typing import Any, ClassVar

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.io import FinishReason

from . import config


class GoogleInteractionsClient(APIMixin):
    """Mixin for Interactions API capabilities.

    Provides shared implementation for all capabilities using the Interactions API:
    - _make_request() - HTTP POST to /v1beta/interactions
    - _make_stream_request() - HTTP streaming to /v1beta/interactions (stream=true in body)
    - _parse_usage() - Extract usage dict from usage metadata
    - _parse_content() - Extract steps array from response
    - _parse_finish_reason() - Extract finish reason (interaction status) from response
    - _content_fields: ClassVar - Content field names to exclude from metadata

    Capability clients extend parsing methods via super() to wrap/transform results.

    Usage:
        class GoogleInteractionsTextClient(GoogleInteractionsMixin, TextClient):
            def _parse_content(self, response_data):
                steps = super()._parse_content(response_data)
                text = "".join(
                    part.get("text", "")
                    for step in steps if step.get("type") == "model_output"
                    for part in step.get("content", [])
                    if part.get("type") == "text"
                )
                return text
    """

    _content_fields: ClassVar[set[str]] = {"steps"}

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
        """Make HTTP request to interactions endpoint."""
        if endpoint is None:
            endpoint = config.GoogleInteractionsEndpoint.CREATE_INTERACTION

        headers = self._json_headers(extra_headers)
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
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Make streaming request to interactions endpoint."""
        if endpoint is None:
            endpoint = config.GoogleInteractionsEndpoint.CREATE_INTERACTION

        headers = self._json_headers(extra_headers)
        return self.http_client.stream_post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map Google Interactions usage fields to unified names.

        Shared by client and streaming across all capabilities.
        """
        return {
            UsageField.INPUT_TOKENS: usage_data.get("total_input_tokens"),
            UsageField.OUTPUT_TOKENS: usage_data.get("total_output_tokens"),
            UsageField.TOTAL_TOKENS: usage_data.get("total_tokens"),
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from Interactions usage metadata."""
        usage_metadata = response_data.get("usage", {})
        return GoogleInteractionsClient.map_usage_fields(usage_metadata)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Return all steps from response.

        Returns list of step objects that capability clients extract content from.
        """
        steps = response_data.get("steps", [])
        if not steps:
            msg = "No steps in response"
            raise ValueError(msg)
        return steps

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Extract finish reason from Interactions response.

        Returns FinishReason that capability clients wrap in their specific type.
        """
        return FinishReason(reason=response_data.get("status"))


__all__ = ["GoogleInteractionsClient"]
