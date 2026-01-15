"""Google Interactions API client mixin."""

from collections.abc import AsyncIterator
from typing import Any

import httpx

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config


class GoogleInteractionsClient(APIMixin):
    """Mixin for Interactions API capabilities.

    Provides shared implementation for all capabilities using the Interactions API:
    - _make_request() - HTTP POST to /v1beta/interactions
    - _make_stream_request() - HTTP streaming to /v1beta/interactions?alt=sse
    - _get_interaction() - HTTP GET to retrieve interaction by ID
    - _parse_usage() - Extract usage dict from usage metadata
    - _parse_content() - Extract outputs array from response
    - _parse_finish_reason() - Extract finish reason string from response
    - _build_metadata() - Filter content fields

    Capability clients extend parsing methods via super() to wrap/transform results.

    Usage:
        class GoogleInteractionsTextGenerationClient(
            GoogleInteractionsClient, TextGenerationClient
        ):
            def _parse_content(self, response_data, **parameters):
                outputs = super()._parse_content(response_data)
                text = "".join(o.get("text", "") for o in outputs if o.get("type") == "text")
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
        """Make HTTP request to interactions endpoint."""
        if endpoint is None:
            endpoint = config.GoogleInteractionsEndpoint.CREATE_INTERACTION

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
        """Make streaming request to interactions endpoint."""
        if endpoint is None:
            endpoint = config.GoogleInteractionsEndpoint.STREAM_INTERACTION

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }
        return self.http_client.stream_post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )

    async def _get_interaction(
        self,
        interaction_id: str,
    ) -> httpx.Response:
        """Get an existing interaction by ID.

        Used for polling background interactions or retrieving previous context.
        """
        endpoint = config.GoogleInteractionsEndpoint.GET_INTERACTION.format(
            interaction_id=interaction_id
        )
        headers = self.auth.get_headers()

        return await self.http_client.get(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
        )

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map Google Interactions usage fields to unified names.

        Shared by client and streaming across all capabilities.
        """
        return {
            UsageField.INPUT_TOKENS: usage_data.get("prompt_token_count"),
            UsageField.OUTPUT_TOKENS: usage_data.get("candidates_token_count"),
            UsageField.TOTAL_TOKENS: usage_data.get("total_token_count"),
            UsageField.REASONING_TOKENS: usage_data.get("thoughts_token_count"),
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from Interactions usage metadata."""
        usage_metadata = response_data.get("usage", {})
        return GoogleInteractionsClient.map_usage_fields(usage_metadata)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Return all outputs from response.

        Returns list of output objects that capability clients extract content from.
        """
        outputs = response_data.get("outputs", [])
        if not outputs:
            msg = "No outputs in response"
            raise ValueError(msg)
        return outputs

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Extract finish reason from Interactions response.

        Returns FinishReason that capability clients wrap in their specific type.
        """
        # Try to find finish_reason at top level or in last output
        reason = response_data.get("finish_reason")
        if not reason:
            outputs = response_data.get("outputs", [])
            if outputs:
                reason = outputs[-1].get("finish_reason")
        return FinishReason(reason=reason)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary, filtering out content fields."""
        content_fields = {"outputs"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)


__all__ = ["GoogleInteractionsClient"]
