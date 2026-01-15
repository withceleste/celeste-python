"""BFL Images API client mixin."""

import asyncio
import time
from collections.abc import AsyncIterator
from typing import Any

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
        class BFLImageGenerationClient(BFLImagesClient, ImageGenerationClient):
            def _parse_content(self, response_data, **parameters):
                result = response_data.get("result", {})
                # Extract image from result["sample"]...
    """

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request with async polling for BFL image generation.

        Handles the complete async polling workflow:
        1. Submit job to /v1/{model_id}
        2. Poll polling_url until Ready/Failed
        3. Return response with _submit_metadata for usage parsing
        """
        auth_headers = self.auth.get_headers()
        headers = {
            **auth_headers,
            "Content-Type": ApplicationMimeType.JSON,
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

        if not polling_url:
            msg = f"No polling_url in {self.provider} response"
            raise ValueError(msg)

        # Phase 2: Poll for completion
        start_time = time.monotonic()
        poll_headers = {
            **auth_headers,
            "Accept": ApplicationMimeType.JSON,
        }

        while True:
            elapsed = time.monotonic() - start_time
            if elapsed >= config.POLLING_TIMEOUT:
                msg = f"{self.provider} polling timed out after {config.POLLING_TIMEOUT} seconds"
                raise TimeoutError(msg)

            poll_response = await self.http_client.get(
                polling_url,
                headers=poll_headers,
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
            elif status in ("Error", "Failed"):
                error_msg = poll_data.get("error", "Unknown error")
                msg = f"{self.provider} image generation failed: {error_msg}"
                raise ValueError(msg)

            await asyncio.sleep(config.POLLING_INTERVAL)

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
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
        """Extract usage data from BFL response."""
        submit_metadata = response_data.get("_submit_metadata", {})
        return BFLImagesClient.map_usage_fields(submit_metadata)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse result from response."""
        result = response_data.get("result", {})
        if not result:
            msg = "No result in response"
            raise ValueError(msg)
        return result

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary, filtering out content fields."""
        content_fields = {"result"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)


__all__ = ["BFLImagesClient"]
