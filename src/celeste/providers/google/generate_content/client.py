"""Google GenerateContent API client mixin."""

from collections.abc import AsyncIterator
from typing import Any

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config


class GoogleGenerateContentClient(APIMixin):
    """Mixin for GenerateContent API capabilities.

    Provides shared implementation for all capabilities using the GenerateContent API:
    - _make_request() - HTTP POST to generateContent
    - _make_stream_request() - HTTP streaming to streamGenerateContent
    - _parse_usage() - Extract usage dict from usageMetadata
    - _parse_content() - Extract parts array from first candidate
    - _parse_finish_reason() - Extract finish reason string from candidates
    - _build_metadata() - Filter content fields

    Capability clients extend parsing methods via super() to wrap/transform results.

    Usage:
        class GoogleTextGenerationClient(GoogleGenerateContentClient, TextGenerationClient):
            def _parse_content(self, response_data, **parameters):
                parts = super()._parse_content(response_data)
                text = parts[0].get("text") or ""
                return self._transform_output(text, **parameters)
    """

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to generateContent endpoint."""
        if endpoint is None:
            endpoint = config.GoogleGenerateContentEndpoint.GENERATE_CONTENT
        endpoint = endpoint.format(model_id=self.model.id)

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
        """Make streaming request to streamGenerateContent endpoint."""
        if endpoint is None:
            endpoint = config.GoogleGenerateContentEndpoint.STREAM_GENERATE_CONTENT
        endpoint = endpoint.format(model_id=self.model.id)

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
        """Map Google Gemini usage fields to unified names.

        Shared by client and streaming across all capabilities.
        """
        return {
            UsageField.INPUT_TOKENS: usage_data.get("promptTokenCount"),
            UsageField.OUTPUT_TOKENS: usage_data.get("candidatesTokenCount"),
            UsageField.TOTAL_TOKENS: usage_data.get("totalTokenCount"),
            UsageField.REASONING_TOKENS: usage_data.get("thoughtsTokenCount"),
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from Gemini usageMetadata."""
        usage_metadata = response_data.get("usageMetadata", {})
        return GoogleGenerateContentClient.map_usage_fields(usage_metadata)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Return all candidates from response.

        Returns list of candidate objects that capability clients extract content from.
        """
        candidates = response_data.get("candidates", [])
        if not candidates:
            msg = "No candidates in response"
            raise ValueError(msg)
        return candidates

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Extract finish reason from Gemini candidates.

        Returns FinishReason that capability clients wrap in their specific type.
        """
        candidates = response_data.get("candidates", [])
        if not candidates:
            reason = None
        else:
            reason = candidates[0].get("finishReason")
        return FinishReason(reason=reason)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary, filtering out content fields."""
        content_fields = {"candidates"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)


__all__ = ["GoogleGenerateContentClient"]
