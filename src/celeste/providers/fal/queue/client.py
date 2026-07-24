"""fal.ai queue API client mixin."""

import asyncio
import time
from collections.abc import AsyncIterator
from typing import Any

from celeste.client import APIMixin
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config


class FalQueueClient(APIMixin):
    """Mixin for fal.ai queue API operations.

    Provides shared implementation:
    - _make_request() - POST to queue, poll status_url, fetch response_url
    - _make_stream_request() - raises StreamingNotSupportedError
    - _parse_usage() - empty (fal queue results carry no usage)
    - _parse_finish_reason() - COMPLETE on success
    - _parse_content() - return completed result payload for modality clients

    The fal queue protocol:
    1. POST https://queue.fal.run/{model_id}
    2. Poll status_url until COMPLETED
    3. GET response_url for the result body
    """

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Submit to fal queue, poll until COMPLETED, return result payload."""
        headers = {
            **self._json_headers(extra_headers),
            "Accept": ApplicationMimeType.JSON,
        }

        if endpoint is None:
            endpoint = config.FalQueueEndpoint.RUN
        endpoint = endpoint.format(model_id=self.model.id)

        submit_response = await self.http_client.post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )
        self._handle_error_response(submit_response)
        submit_data = submit_response.json()

        status_url = submit_data.get("status_url")
        response_url = submit_data.get("response_url")
        if not status_url or not response_url:
            msg = f"No status_url/response_url in {self.provider} response"
            raise ValueError(msg)

        poll_headers = self._merge_headers(
            {**self.auth.get_headers(), "Accept": ApplicationMimeType.JSON},
            extra_headers,
        )
        start_time = time.monotonic()

        while True:
            elapsed = time.monotonic() - start_time
            if elapsed >= config.POLLING_TIMEOUT:
                msg = (
                    f"{self.provider} polling timed out after"
                    f" {config.POLLING_TIMEOUT} seconds"
                )
                raise TimeoutError(msg)

            poll_response = await self.http_client.get(
                status_url,
                headers=poll_headers,
            )
            self._handle_error_response(poll_response)
            poll_data = poll_response.json()
            status = poll_data.get("status")

            if status == "COMPLETED":
                result_response = await self.http_client.get(
                    response_url,
                    headers=poll_headers,
                )
                self._handle_error_response(result_response)
                return result_response.json()

            if status not in ("IN_QUEUE", "IN_PROGRESS"):
                error_msg = poll_data.get("error", poll_data)
                msg = f"{self.provider} request failed: {error_msg}"
                raise ValueError(msg)

            await asyncio.sleep(config.POLLING_INTERVAL)

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """fal queue does not support SSE streaming in this client."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """fal provides no structured finish reason."""
        return FinishReason(reason="COMPLETE")

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """fal queue results do not include usage metrics."""
        return {}

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Return completed queue result payload."""
        return response_data


__all__ = ["FalQueueClient"]
