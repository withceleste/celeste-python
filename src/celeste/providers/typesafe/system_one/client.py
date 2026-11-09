"""TypeSafe System One API client mixin."""

from collections.abc import AsyncGenerator
from typing import Any, ClassVar

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason

from . import config


class TypeSafeSystemOneClient(APIMixin):
    """Mixin for TypeSafe System One API.

    Provides shared HTTP implementation:
    - _build_url(endpoint, streaming) - Apply base_url overrides to both transports
    - _make_request(endpoint=...) - HTTP POST, opting into images when the request needs them
    - _make_stream_request() - raises StreamingNotSupportedError
    - _parse_usage() - Extract usage dict from response
    - _parse_content() - Extract answers map from response
    - _parse_finish_reason() - Extract finish reason (if provided)
    - _content_fields: ClassVar - Content field names to exclude from metadata

    Modality clients set ``_decide_endpoint`` class attribute to route operations.
    """

    _content_fields: ClassVar[set[str]] = {"answers"}

    def _build_url(self, endpoint: str, streaming: bool = False) -> str:
        """Build the request URL, honoring an explicit base_url override."""
        base = self.base_url if self.base_url is not None else config.BASE_URL
        return f"{base.rstrip('/')}{endpoint}"

    def _build_request(
        self,
        inputs: Any,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Build request with model ID."""
        request_body = super()._build_request(
            inputs, extra_body=extra_body, streaming=streaming, **parameters
        )
        request_body["model"] = self.model.id
        return request_body

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request to TypeSafe System One API."""
        if endpoint is None:
            endpoint = config.TypeSafeSystemOneEndpoint.CREATE_DECISION

        # TypeSafe rejects image assets and box questions without this opt-in header.
        if request_body.get("assets") or any(
            question.get("type") == "box"
            for question in request_body.get("questions", {}).values()
        ):
            extra_headers = {
                config.HEADER_TYPESAFE_DANGER_ZONE_IMAGES: "true",
                **(extra_headers or {}),
            }
        headers = await self._json_headers(extra_headers)

        response = await self.http_client.post(
            self._build_url(endpoint),
            headers=headers,
            json_body=request_body,
        )
        self._handle_error_response(response)
        data: dict[str, Any] = response.json()
        return data

    async def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """TypeSafe System One does not support SSE streaming in this client."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map TypeSafe System One usage fields to unified names."""
        return {
            UsageField.INPUT_TOKENS: usage_data.get("input_tokens"),
            UsageField.OUTPUT_TOKENS: usage_data.get("output_tokens"),
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from TypeSafe System One API response."""
        usage_data = response_data.get("usage") or {}
        return TypeSafeSystemOneClient.map_usage_fields(usage_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse answers map from TypeSafe System One API response."""
        answers = response_data.get("answers")
        if not answers:
            msg = "No answers in response"
            raise ValueError(msg)
        return answers

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """TypeSafe System One API doesn't provide finish reasons."""
        return FinishReason(reason=None)


__all__ = ["TypeSafeSystemOneClient"]
