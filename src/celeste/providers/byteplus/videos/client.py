"""BytePlus Videos API client mixin."""

import asyncio
import logging
import time
from collections.abc import AsyncIterator
from typing import Any

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config

logger = logging.getLogger(__name__)


class BytePlusVideosClient(APIMixin):
    """Mixin for BytePlus ModelArk Videos API with async polling.

    Provides shared implementation:
    - _make_request() - HTTP POST with async polling pattern

    The BytePlus Videos API uses async polling:
    1. POST to /api/v3/contents/generations/tasks to submit job
    2. Poll GET /api/v3/contents/generations/tasks/{task_id} until succeeded/failed
    3. Return final response

    Usage:
        class BytePlusVideoGenerationClient(BytePlusVideosClient, VideoGenerationClient):
            def _parse_content(self, response_data, **parameters):
                content = response_data.get("content", {})
                # Extract video from content["video_url"]...
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
        """Make HTTP request with async polling for BytePlus video generation.

        Handles the complete async polling workflow:
        1. Submit job to CONTENT_GENERATIONS endpoint
        2. Poll CONTENT_STATUS endpoint until succeeded/failed/canceled
        3. Return response with final status data
        """
        auth_headers = self.auth.get_headers()
        headers = {
            **auth_headers,
            "Content-Type": ApplicationMimeType.JSON,
        }

        if endpoint is None:
            endpoint = config.BytePlusVideosEndpoint.CREATE_VIDEO

        # Phase 1: Submit job
        logger.debug("Submitting video generation task to BytePlus")
        submit_response = await self.http_client.post(
            f"{config.BASE_URL}{endpoint}",
            headers=headers,
            json_body=request_body,
        )

        self._handle_error_response(submit_response)
        submit_data = submit_response.json()
        task_id = submit_data["id"]
        logger.info(f"BytePlus task submitted: {task_id}")

        # Phase 2: Poll for completion
        start_time = time.monotonic()

        # Wait before first poll
        await asyncio.sleep(config.POLLING_INTERVAL)

        while True:
            elapsed = time.monotonic() - start_time
            if elapsed >= config.POLLING_TIMEOUT:
                msg = f"BytePlus task {task_id} timed out after {config.POLLING_TIMEOUT} seconds"
                raise TimeoutError(msg)

            status_url = f"{config.BASE_URL}{config.BytePlusVideosEndpoint.GET_VIDEO_STATUS.format(task_id=task_id)}"
            logger.debug(f"Polling BytePlus task status: {task_id}")

            status_response = await self.http_client.get(
                status_url,
                headers=headers,
            )

            self._handle_error_response(status_response)
            status_data: dict[str, Any] = status_response.json()
            status = status_data.get("status")
            logger.debug(f"BytePlus task {task_id} status: {status}")

            if status == config.STATUS_SUCCEEDED:
                logger.info(f"BytePlus task {task_id} completed in {elapsed:.0f}s")
                return status_data

            if status in (config.STATUS_FAILED, config.STATUS_CANCELED):
                error = status_data.get("error", {})
                error_msg = (
                    error.get("message", "Unknown error")
                    if isinstance(error, dict)
                    else "Unknown error"
                )
                msg = f"BytePlus task {task_id} failed: {error_msg}"
                raise ValueError(msg)

            await asyncio.sleep(config.POLLING_INTERVAL)

    def _make_stream_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """BytePlus Videos API does not support SSE streaming in this client."""
        raise StreamingNotSupportedError(model_id=self.model.id)

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, int | float | None]:
        """Map BytePlus Videos usage fields to unified names.

        Shared by client and streaming across all capabilities.
        """
        return {
            UsageField.TOTAL_TOKENS: usage_data.get("total_tokens"),
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Extract usage data from BytePlus API response."""
        usage_data = response_data.get("usage", {})
        return BytePlusVideosClient.map_usage_fields(usage_data)

    def _parse_content(self, response_data: dict[str, Any]) -> Any:
        """Parse content from BytePlus video generation response."""
        content = response_data.get("content", {})
        if not content:
            msg = "No content in response"
            raise ValueError(msg)
        return content

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """BytePlus provides status but not structured finish reasons."""
        return FinishReason(reason=None)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary, filtering out content fields."""
        content_fields = {"content"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        return super()._build_metadata(filtered_data)


__all__ = ["BytePlusVideosClient"]
