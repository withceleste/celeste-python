"""OpenAI client implementation for video generation."""

import asyncio
import base64
import io
import json
import logging
from typing import Any, Unpack

import httpx
from PIL import Image

from celeste.artifacts import ImageArtifact, VideoArtifact
from celeste.exceptions import ValidationError
from celeste.mime_types import ApplicationMimeType, VideoMimeType
from celeste.parameters import ParameterMapper
from celeste_video_generation.client import VideoGenerationClient
from celeste_video_generation.io import (
    VideoGenerationInput,
    VideoGenerationUsage,
)
from celeste_video_generation.parameters import VideoGenerationParameters

from . import config
from .parameters import OPENAI_PARAMETER_MAPPERS

logger = logging.getLogger(__name__)


class OpenAIVideoGenerationClient(VideoGenerationClient):
    """OpenAI client for video generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return OPENAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: VideoGenerationInput) -> dict[str, Any]:
        """Initialize request from OpenAI API format."""
        request = {
            "prompt": inputs.prompt,
            "model": self.model.id,
        }

        return request

    def _build_request(
        self,
        inputs: VideoGenerationInput,
        **parameters: Unpack[VideoGenerationParameters],
    ) -> dict[str, Any]:
        """Build request with parameter mapping and size derivation."""
        request = super()._build_request(inputs, **parameters)

        aspect_ratio = parameters.get("aspect_ratio")
        resolution = parameters.get("resolution")

        if bool(aspect_ratio) != bool(resolution):
            msg = (
                "Both aspect_ratio and resolution must be specified together. "
                f"Got aspect_ratio={aspect_ratio!r}, resolution={resolution!r}"
            )
            raise ValidationError(msg)

        if aspect_ratio and resolution:
            ASPECT_RATIO_MAP = {
                ("16:9", "720p"): "1280x720",
                ("9:16", "720p"): "720x1280",
            }

            size = ASPECT_RATIO_MAP.get((aspect_ratio, resolution))
            if size:
                request["size"] = size

        return request

    def _parse_usage(self, response_data: dict[str, Any]) -> VideoGenerationUsage:
        """Parse usage from response."""
        seconds = response_data.get("seconds")
        return VideoGenerationUsage(
            billing_units=float(seconds) if seconds else None,
        )

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[VideoGenerationParameters],
    ) -> VideoArtifact:
        """Parse content from response."""
        video_data_b64 = response_data["video_data"]
        video_data = base64.b64decode(video_data_b64)
        return VideoArtifact(
            data=video_data,
            mime_type=VideoMimeType.MP4,
        )

    async def _prepare_multipart_request(
        self,
        request_body: dict[str, Any],
    ) -> tuple[dict[str, tuple[str, bytes, str]], dict[str, str]]:
        """Prepare multipart form data from request_body with input_reference."""
        size = request_body.get("size", "720x1280")

        input_reference = request_body.pop("input_reference", None)
        if input_reference is None:
            return {}, {}

        if not isinstance(input_reference, ImageArtifact):
            msg = f"input_reference must be ImageArtifact, got {type(input_reference).__name__}"
            raise ValueError(msg)

        if input_reference.data:
            image_data = input_reference.data
        elif input_reference.path:
            with open(input_reference.path, "rb") as f:
                image_data = f.read()
        else:
            msg = "ImageArtifact must have data or path for input_reference"
            raise ValueError(msg)

        img = Image.open(io.BytesIO(image_data))
        actual_size = f"{img.width}x{img.height}"
        if actual_size != size:
            msg = (
                f"Image dimensions ({actual_size}) must match video size ({size}). "
                f"Please resize your image to {size} before uploading."
            )
            raise ValueError(msg)

        mime_type = (
            input_reference.mime_type.value
            if input_reference.mime_type
            else "image/jpeg"
        )

        files = {
            "input_reference": ("image.jpg", image_data, mime_type),
        }

        data = {
            k: str(v) if isinstance(v, (str, int, float)) else json.dumps(v)
            for k, v in request_body.items()
        }

        return files, data

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[VideoGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request with async polling for OpenAI video generation."""
        headers = {
            config.AUTH_HEADER_NAME: f"{config.AUTH_HEADER_PREFIX}{self.api_key.get_secret_value()}",
        }

        files, data = await self._prepare_multipart_request(request_body.copy())

        if files:
            logger.info("Sending multipart request to OpenAI with input_reference")
            response = await self.http_client.post_multipart(
                f"{config.BASE_URL}{config.ENDPOINT}",
                headers=headers,
                files=files,
                data=data,
            )
        else:
            logger.info(f"Sending request to OpenAI: {request_body}")
            response = await self.http_client.post(
                f"{config.BASE_URL}{config.ENDPOINT}",
                headers=headers,
                json_body=request_body,
            )
        self._handle_error_response(response)
        video_obj = response.json()

        video_id = video_obj["id"]
        logger.info(f"Created video job: {video_id}")

        for _ in range(config.MAX_POLLS):
            status_response = await self.http_client.get(
                f"{config.BASE_URL}{config.ENDPOINT}/{video_id}",
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

        content_response = await self.http_client.get(
            f"{config.BASE_URL}{config.ENDPOINT}/{video_id}{config.CONTENT_ENDPOINT_SUFFIX}",
            headers=headers,
        )
        self._handle_error_response(content_response)
        video_data = content_response.content

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

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata from response data."""
        content_fields = {"video_data"}
        filtered_data = {
            k: v for k, v in response_data.items() if k not in content_fields
        }
        metadata = super()._build_metadata(filtered_data)
        metadata["video_id"] = response_data.get("video_id")
        metadata["seconds"] = response_data.get("seconds")
        metadata["size"] = response_data.get("size")
        metadata["created_at"] = response_data.get("created_at")
        metadata["completed_at"] = response_data.get("completed_at")
        metadata["expires_at"] = response_data.get("expires_at")
        return metadata


__all__ = ["OpenAIVideoGenerationClient"]
