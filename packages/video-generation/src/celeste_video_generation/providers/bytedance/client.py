"""ByteDance client implementation for video generation."""

import asyncio
import base64
import json
import logging
import time
from typing import Any, Unpack

import httpx

from celeste.artifacts import ImageArtifact, VideoArtifact
from celeste.mime_types import ApplicationMimeType, VideoMimeType
from celeste.parameters import ParameterMapper
from celeste_video_generation.client import VideoGenerationClient
from celeste_video_generation.io import (
    VideoGenerationInput,
    VideoGenerationUsage,
)
from celeste_video_generation.parameters import VideoGenerationParameters

from . import config
from .parameters import BYTEDANCE_PARAMETER_MAPPERS

logger = logging.getLogger(__name__)


class ByteDanceVideoGenerationClient(VideoGenerationClient):
    """ByteDance client for video generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return BYTEDANCE_PARAMETER_MAPPERS

    def _validate_artifacts(
        self,
        inputs: VideoGenerationInput,
        **parameters: Unpack[VideoGenerationParameters],
    ) -> tuple[VideoGenerationInput, dict[str, Any]]:
        """Validate and prepare artifacts for ByteDance API."""

        # Helper function to convert ImageArtifact to base64 data URI
        def convert_to_data_url(img: ImageArtifact) -> ImageArtifact:
            if img.url:
                return img
            elif img.data:
                file_data = img.data
            elif img.path:
                with open(img.path, "rb") as f:
                    file_data = f.read()
            else:
                msg = "ImageArtifact must have url, data, or path"
                raise ValueError(msg)

            base64_data = base64.b64encode(file_data).decode("utf-8")
            mime_type = img.mime_type.value if img.mime_type else "image/jpeg"

            return ImageArtifact(
                url=f"data:{mime_type};base64,{base64_data}",
                mime_type=img.mime_type,
                metadata=img.metadata,
            )

        reference_images = parameters.get("reference_images")
        if reference_images:
            converted_images = [convert_to_data_url(img) for img in reference_images]
            parameters["reference_images"] = converted_images

        first_frame = parameters.get("first_frame")
        if first_frame:
            parameters["first_frame"] = convert_to_data_url(first_frame)

        last_frame = parameters.get("last_frame")
        if last_frame:
            parameters["last_frame"] = convert_to_data_url(last_frame)

        return inputs, dict(parameters)

    def _add_image_content_item(
        self,
        content: list[dict[str, Any]],
        artifact: ImageArtifact | VideoArtifact,
        role: str,
        artifact_type: str,
    ) -> None:
        """Add image content item to content array."""
        if artifact.url:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": artifact.url,
                    },
                    "role": role,
                }
            )
        elif artifact.data:
            logger.warning(
                f"ByteDance requires {artifact_type} URL, not base64 data. Upload {artifact_type} first."
            )
        elif artifact.path:
            logger.warning(
                f"ByteDance requires {artifact_type} URL, not file path. Upload {artifact_type} first."
            )

    def _init_request(self, inputs: VideoGenerationInput) -> dict[str, Any]:
        """Initialize request from BytePlus ModelArk API format."""
        content: list[dict[str, Any]] = [
            {
                "type": "text",
                "text": inputs.prompt,
            }
        ]

        request: dict[str, Any] = {
            "model": self.model.id,
            "content": content,
        }

        return request

    def _parse_usage(self, response_data: dict[str, Any]) -> VideoGenerationUsage:
        """Parse usage from response."""
        usage_data = response_data.get("usage", {})
        total_tokens = usage_data.get("total_tokens")

        return VideoGenerationUsage(
            total_tokens=total_tokens,
        )

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[VideoGenerationParameters],
    ) -> VideoArtifact:
        """Parse content from response."""
        content = response_data.get("content")
        if not isinstance(content, dict):
            msg = f"No content field in ByteDance response. Available keys: {list(response_data.keys())}"
            raise ValueError(msg)

        video_url = content.get("video_url")
        if not video_url:
            msg = f"No video_url in content field. Available content keys: {list(content.keys())}"
            raise ValueError(msg)

        return VideoArtifact(
            url=video_url,
            mime_type=VideoMimeType.MP4,
        )

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        content_fields = {"content"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        metadata = super()._build_metadata(filtered_data)

        task_id = response_data.get("id")
        if task_id:
            metadata["task_id"] = task_id

        status = response_data.get("status")
        if status:
            metadata["status"] = status

        content = response_data.get("content")
        if isinstance(content, dict):
            last_frame_url = content.get("last_frame_url")
            if last_frame_url:
                metadata["last_frame_url"] = last_frame_url

        return metadata

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[VideoGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request with async polling."""
        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
            "Content-Type": ApplicationMimeType.JSON,
        }

        logger.debug("Submitting video generation task to ByteDance")
        submit_response = await self.http_client.post(
            f"{config.BASE_URL}{config.ENDPOINT}",
            headers=headers,
            json_body=request_body,
        )
        self._handle_error_response(submit_response)
        submit_data = submit_response.json()

        task_id = submit_data["id"]
        logger.info(f"ByteDance task submitted: {task_id}")

        start_time = time.time()
        polling_interval = config.DEFAULT_POLLING_INTERVAL

        # Wait before first poll (consistent with Google pattern)
        await asyncio.sleep(polling_interval)

        while True:
            elapsed = time.time() - start_time
            if elapsed > config.MAX_POLLING_TIMEOUT:
                msg = f"ByteDance task {task_id} timed out after {elapsed:.0f}s"
                raise TimeoutError(msg)

            status_url = f"{config.BASE_URL}{config.STATUS_ENDPOINT_TEMPLATE.format(task_id=task_id)}"
            logger.debug(f"Polling ByteDance task status: {task_id}")

            status_response = await self.http_client.get(
                status_url,
                headers=headers,
            )
            self._handle_error_response(status_response)
            status_data = status_response.json()

            status = status_data.get("status")
            logger.debug(f"ByteDance task {task_id} status: {status}")

            if status == config.STATUS_SUCCEEDED:
                logger.info(f"ByteDance task {task_id} completed in {elapsed:.0f}s")
                return httpx.Response(
                    200,
                    content=json.dumps(status_data).encode(),
                    headers={"Content-Type": ApplicationMimeType.JSON},
                )

            if status in [config.STATUS_FAILED, config.STATUS_CANCELED]:
                error = status_data.get("error", {})
                error_msg = (
                    error.get("message", "Unknown error")
                    if isinstance(error, dict)
                    else "Unknown error"
                )
                msg = f"ByteDance task {task_id} failed: {error_msg}"
                raise ValueError(msg)

            await asyncio.sleep(polling_interval)


__all__ = ["ByteDanceVideoGenerationClient"]
