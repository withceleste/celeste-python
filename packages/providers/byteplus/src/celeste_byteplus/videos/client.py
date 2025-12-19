"""BytePlus Videos API client with shared implementation."""

import asyncio
import logging
import time
from typing import Any

import httpx

from celeste.client import APIMixin
from celeste.core import UsageField
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

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Any,
    ) -> httpx.Response:
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

        # Phase 1: Submit job
        logger.debug("Submitting video generation task to BytePlus")
        submit_response = await self.http_client.post(
            f"{config.BASE_URL}{config.BytePlusVideosEndpoint.CREATE_VIDEO}",
            headers=headers,
            json_body=request_body,
        )

        if submit_response.status_code != 200:
            return submit_response

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

            if status_response.status_code != 200:
                return status_response

            status_data = status_response.json()
            status = status_data.get("status")
            logger.debug(f"BytePlus task {task_id} status: {status}")

            if status == config.STATUS_SUCCEEDED:
                logger.info(f"BytePlus task {task_id} completed in {elapsed:.0f}s")
                return httpx.Response(
                    status_code=200,
                    json=status_data,
                    request=httpx.Request("GET", status_url),
                )

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

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, Any]:
        """Map BytePlus Videos usage fields to unified names.

        Shared by client and streaming across all capabilities.
        """
        return {
            UsageField.TOTAL_TOKENS: usage_data.get("total_tokens"),
        }

    def _parse_usage(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Extract usage data from BytePlus API response."""
        usage_data = response_data.get("usage", {})
        return BytePlusVideosClient.map_usage_fields(usage_data)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """BytePlus provides status but not structured finish reasons."""
        return FinishReason(reason=None)


__all__ = ["BytePlusVideosClient"]
