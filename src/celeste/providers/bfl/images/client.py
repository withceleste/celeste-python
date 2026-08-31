"""BFL Images API client mixin."""

import asyncio
import time
from collections.abc import AsyncIterator
from typing import Any, ClassVar

import httpx

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config


class BFLImagesClient(APIMixin):
    """Mixin for BFL Images API operations.

    Provides shared implementation:
    - _make_request() - HTTP POST with async polling pattern
    - _parse_finish_reason() - Map BFL status to FinishReason

    The BFL API uses async polling:
    1. POST to /v1/{model_id} to submit job
    2. Poll GET polling_url until Ready/Failed
    3. Return final response with merged metadata

    Usage:
        class BFLImagesClient(BFLImagesMixin, ImagesClient):
            def _parse_content(self, response_data):
                result = response_data.get("result", {})
                # Extract image from result["sample"]...
    """

    _content_fields: ClassVar[set[str]] = {"result"}

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request with async polling for BFL image generation.

        Handles the complete async polling workflow:
        1. Submit job to /v1/{model_id}
        2. Poll polling_url until Ready/Failed
        3. Return response with _submit_metadata for usage parsing
        """
        headers = {
            **self._json_headers(extra_headers),
            "Accept": ApplicationMimeType.JSON,
        }

        if endpoint is None:
            endpoint = config.BFLImagesEndpoint.CREATE_IMAGE
        endpoint = endpoint.format(model_id=self.model.id)

        # Phase 1: Submit job
        submit_response = await self.http_client.post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )

        self._handle_error_response(submit_response)
        submit_data = submit_response.json()
        polling_url = submit_data.get("polling_url")

        if not isinstance(polling_url, str) or not polling_url:
            msg = f"No polling_url in {self.provider} response"
            raise ValueError(msg)

        parsed_url = httpx.URL(polling_url)
        if (
            parsed_url.scheme != "https"
            or parsed_url.host not in {"api.bfl.ai", "api.eu.bfl.ai", "api.us.bfl.ai"}
            or parsed_url.port not in {None, 443}
            or parsed_url.username
            or parsed_url.password
        ):
            msg = f"Untrusted polling_url in {self.provider} response"
            raise ValueError(msg)

        # Phase 2: Poll for completion
        start_time = time.monotonic()
        poll_headers = self._merge_headers(
            {**self.auth.get_headers(), "Accept": ApplicationMimeType.JSON},
            extra_headers,
        )

        while True:
            elapsed = time.monotonic() - start_time
            if elapsed >= config.POLLING_TIMEOUT:
                msg = f"{self.provider} polling timed out after {config.POLLING_TIMEOUT} seconds"
                raise TimeoutError(msg)

            poll_response = await self.http_client.get(
                polling_url,
                headers=poll_headers,
                follow_redirects=False,
            )

            self._handle_error_response(poll_response)
            poll_data = poll_response.json()
            status = poll_data.get("status")

            if status == "Ready":
                # Merge submit metadata into final response for usage parsing
                return {
                    **poll_data,
                    "_submit_metadata": submit_data,
                }
            elif status in (
                "Error",
                "Failed",
                "Request Moderated",
                "Content Moderated",
                "Task not found",
            ):
                error_msg = poll_data.get("error") or poll_data.get("details") or status
                msg = f"{self.provider} image generation failed ({status}): {error_msg}"
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
        """BFL Images API does not support SSE streaming in this client."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """BFL provides status but not structured finish reasons."""
        return FinishReason(reason=None)

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map BFL usage fields to unified names.

        Shared by client and streaming across all capabilities.
        """
        cost = usage_data.get("cost")
        input_mp = usage_data.get("input_mp")
        output_mp = usage_data.get("output_mp")
        return {
            UsageField.BILLED_UNITS: float(cost) if cost is not None else None,
            UsageField.INPUT_MP: float(input_mp) if input_mp is not None else None,
            UsageField.OUTPUT_MP: float(output_mp) if output_mp is not None else None,
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Prefer settled credits and retain submission megapixel telemetry."""
        usage_data = dict(response_data.get("_submit_metadata", {}))
        if response_data.get("cost") is not None:
            usage_data["cost"] = response_data["cost"]
        return BFLImagesClient.map_usage_fields(usage_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse result from response."""
        result = response_data.get("result", {})
        if not result:
            msg = "No result in response"
            raise ValueError(msg)
        return result


__all__ = ["BFLImagesClient"]
