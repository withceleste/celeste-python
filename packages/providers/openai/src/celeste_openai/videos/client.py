"""OpenAI Videos API client mixin.

Provides shared implementation for capabilities using the OpenAI Videos API:
- video-generation (async polling pattern)
"""

import asyncio
import base64
import json
import logging
from typing import Any

import httpx

from celeste.client import APIMixin
from celeste.core import UsageField
from celeste.io import FinishReason
from celeste.mime_types import ApplicationMimeType

from . import config

logger = logging.getLogger(__name__)


class OpenAIVideosClient(APIMixin):
    """Mixin for OpenAI Videos API video generation.

    Provides shared implementation for video generation:
    - _make_request() - HTTP POST with async polling pattern
    - _parse_usage() - Returns billing units from response
    - _parse_finish_reason() - Returns None (Videos API doesn't provide finish reasons)
    - _build_metadata() - Filter content fields, include video metadata

    The Videos API uses async polling:
    1. POST to create video job at /v1/videos
    2. Poll GET /v1/videos/{id} until completed/failed
    3. GET /v1/videos/{id}/content to retrieve video data

    Usage:
        class OpenAIVideoGenerationClient(OpenAIVideosClient, VideoGenerationClient):
            async def _prepare_multipart_request(self, request_body):
                # Handle input_reference image uploads...
    """

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Any,
    ) -> httpx.Response:
        """Make HTTP request with async polling for OpenAI video generation.

        Handles the complete async polling workflow:
        1. Create video job
        2. Poll for completion
        3. Fetch video content
        """
        request_body["model"] = self.model.id

        headers = {
            **self.auth.get_headers(),
            "Content-Type": ApplicationMimeType.JSON,
        }

        files, data = await self._prepare_multipart_request(request_body.copy())

        endpoint = config.OpenAIVideosEndpoint.CREATE_VIDEO

        if files:
            logger.info("Sending multipart request to OpenAI with input_reference")
            response = await self.http_client.post_multipart(
                f"{config.BASE_URL}{endpoint}",
                headers=headers,
                files=files,
                data=data,
            )
        else:
            logger.info(f"Sending request to OpenAI: {request_body}")
            response = await self.http_client.post(
                f"{config.BASE_URL}{endpoint}",
                headers=headers,
                json_body=request_body,
            )

        self._handle_error_response(response)
        video_obj = response.json()

        video_id = video_obj["id"]
        logger.info(f"Created video job: {video_id}")

        # Poll for completion
        for _ in range(config.MAX_POLLS):
            status_response = await self.http_client.get(
                f"{config.BASE_URL}{endpoint}/{video_id}",
                headers=headers,
            )
            self._handle_error_response(status_response)
            video_obj = status_response.json()

            status = video_obj["status"]
            progress = video_obj.get("progress", 0)

            logger.info(f"Video {video_id}: {status} ({progress}%)")

            if status == config.STATUS_COMPLETED:
                break
            elif status == config.STATUS_FAILED:
                error = video_obj.get("error", {})
                msg = (
                    f"Video generation failed: {error.get('message', 'Unknown error')}"
                )
                raise RuntimeError(msg)

            await asyncio.sleep(config.POLL_INTERVAL)
        else:
            msg = f"Video generation timeout after {config.MAX_POLLS * config.POLL_INTERVAL} seconds"
            raise TimeoutError(msg)

        # Fetch video content
        content_response = await self.http_client.get(
            f"{config.BASE_URL}{endpoint}/{video_id}{config.CONTENT_ENDPOINT_SUFFIX}",
            headers=headers,
        )
        self._handle_error_response(content_response)
        video_data = content_response.content

        # Build normalized response
        response_data = {
            "video_data": base64.b64encode(video_data).decode("utf-8"),
            "model": video_obj.get("model", self.model.id),
            "video_id": video_id,
            "seconds": video_obj.get("seconds"),
            "size": video_obj.get("size"),
            "created_at": video_obj.get("created_at"),
            "completed_at": video_obj.get("completed_at"),
            "expires_at": video_obj.get("expires_at"),
        }

        return httpx.Response(
            200,
            content=json.dumps(response_data).encode(),
            headers={"Content-Type": ApplicationMimeType.JSON},
        )

    async def _prepare_multipart_request(
        self,
        request_body: dict[str, Any],
    ) -> tuple[dict[str, tuple[str, bytes, str]], dict[str, str]]:
        """Prepare multipart form data from request_body.

        Override in capability client to handle input_reference or other file uploads.
        Default implementation returns empty dicts (no file uploads).
        """
        return {}, {}

    @staticmethod
    def map_usage_fields(usage_data: dict[str, Any]) -> dict[str, Any]:
        """Map OpenAI Videos usage fields to unified names.

        Shared by client and streaming across all capabilities.
        Videos API uses billing units (seconds), not tokens.
        """
        return {
            UsageField.BILLED_UNITS: usage_data.get("seconds"),
        }

    def _parse_usage(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Extract usage data from Videos API response."""
        return OpenAIVideosClient.map_usage_fields(response_data)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> FinishReason:
        """Videos API doesn't provide finish reasons."""
        return FinishReason(reason=None)

    def _build_metadata(self, response_data: dict[str, Any]) -> Any:
        """Build metadata dictionary, including video-specific fields."""
        content_fields = {"video_data"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }

        metadata = super()._build_metadata(filtered_data)

        return metadata


__all__ = ["OpenAIVideosClient"]
