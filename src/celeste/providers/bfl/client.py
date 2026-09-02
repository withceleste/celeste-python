"""Shared BFL asynchronous API client."""

import asyncio
import time
from collections.abc import AsyncIterator
from typing import Any, ClassVar

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

_BASE_URL = "https://api.bfl.ai"
_TERMINAL_FAILURES = frozenset(
    {
        "Error",
        "Failed",
        "Request Moderated",
        "Content Moderated",
        "Task not found",
    }
)


class BFLAsyncClient(APIMixin):
    """Shared submit-and-poll implementation for BFL APIs."""

    _content_fields: ClassVar[set[str]] = {"result"}
    _default_endpoint: ClassVar[str]
    _operation_label: ClassVar[str] = "generation"
    _polling_interval: ClassVar[float]
    _polling_timeout: ClassVar[float]

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Submit a BFL job and poll its returned URL until completion."""
        headers = {
            **self._json_headers(extra_headers),
            "Accept": ApplicationMimeType.JSON,
        }
        endpoint = (endpoint or self._default_endpoint).format(model_id=self.model.id)
        submit_response = await self.http_client.post(
            f"{_BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )
        self._handle_error_response(submit_response)
        submit_data: dict[str, Any] = submit_response.json()
        polling_url = submit_data.get("polling_url")
        if not isinstance(polling_url, str) or not polling_url:
            msg = f"No polling_url in {self.provider} response"
            raise ValueError(msg)

        poll_headers = self._merge_headers(
            {**self.auth.get_headers(), "Accept": ApplicationMimeType.JSON},
            extra_headers,
        )
        started = time.monotonic()
        while time.monotonic() - started < self._polling_timeout:
            poll_response = await self.http_client.get(
                polling_url,
                headers=poll_headers,
            )
            self._handle_error_response(poll_response)
            poll_data: dict[str, Any] = poll_response.json()
            status = poll_data.get("status")
            if status == "Ready":
                return {**poll_data, "_submit_metadata": submit_data}
            if status in _TERMINAL_FAILURES:
                detail = poll_data.get("error") or poll_data.get("details") or status
                msg = f"{self.provider} {self._operation_label} failed ({status}): {detail}"
                raise ValueError(msg)
            await asyncio.sleep(self._polling_interval)

        msg = f"{self.provider} polling timed out after {self._polling_timeout} seconds"
        raise TimeoutError(msg)

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Reject SSE streaming, which BFL's asynchronous APIs do not expose."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map BFL credits and megapixels to unified usage fields."""
        return {
            UsageField.BILLED_UNITS: _float_or_none(usage_data.get("cost")),
            UsageField.INPUT_MP: _float_or_none(usage_data.get("input_mp")),
            UsageField.OUTPUT_MP: _float_or_none(usage_data.get("output_mp")),
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Prefer settled poll usage and fall back to submission estimates."""
        usage_data = dict(response_data.get("_submit_metadata", {}))
        for field in ("cost", "input_mp", "output_mp"):
            if response_data.get(field) is not None:
                usage_data[field] = response_data[field]
        return self.map_usage_fields(usage_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Return the non-empty BFL result object."""
        result = response_data.get("result")
        if not result:
            msg = "No result in response"
            raise ValueError(msg)
        return result

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Return an empty finish reason because BFL only exposes task status."""
        return FinishReason(reason=None)


def _float_or_none(value: object) -> float | None:
    """Convert an optional numeric BFL usage value to float."""
    return float(value) if value is not None else None


__all__ = ["BFLAsyncClient"]
