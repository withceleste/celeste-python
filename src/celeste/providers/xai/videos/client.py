"""xAI Videos API client mixin."""

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config


class XAIVideosClient(APIMixin):
    """Mixin for xAI Videos API video generation.

    Provides shared implementation for video generation:
    - _make_request() - HTTP POST with async polling pattern
    - _parse_usage() - Extract usage dict from response
    - _parse_content() - Extract video URL from response
    - _parse_finish_reason() - Returns None (Videos API doesn't provide finish reasons)
    - _build_metadata() - Filter content fields

    The Videos API uses async polling:
    1. POST to /v1/videos/generations returns request_id
    2. Poll GET /v1/videos/{request_id} until completed/failed
    3. Response contains video URL directly
    """

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

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """xAI Videos API does not support SSE streaming."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> dict[str, Any]:
        """Make HTTP request with async polling for xAI video generation."""
        if endpoint is None:
            endpoint = config.XAIVideosEndpoint.CREATE_VIDEO

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        # Submit video generation request
        response = await self.http_client.post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )
        self._handle_error_response(response)
        video_obj: dict[str, Any] = response.json()

        request_id = video_obj.get("request_id")
        if not request_id:
            # Response already has URL (e.g., cached result)
            if "url" in video_obj:
                return video_obj
            msg = "No request_id in video generation response"
            raise ValueError(msg)

        # Poll for completion
        poll_endpoint = f"/v1/videos/{request_id}"
        for _ in range(config.MAX_POLLS):
            await asyncio.sleep(config.POLL_INTERVAL)

            status_response = await self.http_client.get(
                f"{config.BASE_URL}{poll_endpoint}",
                headers=headers,
            )
            self._handle_error_response(status_response)

            # xAI uses HTTP status codes: 200 = ready, 202 = still processing
            if status_response.status_code == 200:
                return status_response.json()

            # 202 Accepted means still processing, continue polling
            if status_response.status_code == 202:
                continue

            # Parse response for error handling
            video_obj = status_response.json()
            status = video_obj.get("status", "")
            if status == config.STATUS_FAILED:
                error = video_obj.get("error", "Video generation failed")
                raise RuntimeError(error)

        msg = f"Video generation timeout after {config.MAX_POLLS * config.POLL_INTERVAL} seconds"
        raise TimeoutError(msg)

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map xAI Videos usage fields to unified names."""
        return {
            UsageField.INPUT_TOKENS: usage_data.get("input_tokens"),
            UsageField.OUTPUT_TOKENS: usage_data.get("output_tokens"),
            UsageField.TOTAL_TOKENS: usage_data.get("total_tokens"),
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from xAI Videos API response."""
        usage_data = response_data.get("usage", {})
        return XAIVideosClient.map_usage_fields(usage_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse video URL from xAI Videos API response.

        Response structure: {"video": {"url": "...", "duration": 8}, "model": "..."}
        """
        video = response_data.get("video", {})
        url = video.get("url")
        if not url:
            msg = "No video URL in response"
            raise ValueError(msg)
        return url

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Videos API doesn't provide finish reasons."""
        return FinishReason(reason=None)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary, filtering out content fields."""
        content_fields = {"video"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)


__all__ = ["XAIVideosClient"]
