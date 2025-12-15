"""BytePlus client implementation for video generation."""

import base64
import logging
from typing import Any, Unpack

from celeste_byteplus.videos.client import BytePlusVideosClient

from celeste.artifacts import ImageArtifact, VideoArtifact
from celeste.mime_types import VideoMimeType
from celeste.parameters import ParameterMapper
from celeste_video_generation.client import VideoGenerationClient
from celeste_video_generation.io import (
    VideoGenerationInput,
    VideoGenerationUsage,
)
from celeste_video_generation.parameters import VideoGenerationParameters

from .parameters import BYTEPLUS_PARAMETER_MAPPERS

logger = logging.getLogger(__name__)


class BytePlusVideoGenerationClient(BytePlusVideosClient, VideoGenerationClient):
    """BytePlus client for video generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return BYTEPLUS_PARAMETER_MAPPERS

    def _validate_artifacts(
        self,
        inputs: VideoGenerationInput,
        **parameters: Unpack[VideoGenerationParameters],
    ) -> tuple[VideoGenerationInput, dict[str, Any]]:
        """Validate and prepare artifacts for BytePlus API."""

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
                f"BytePlus requires {artifact_type} URL, not base64 data. Upload {artifact_type} first."
            )
        elif artifact.path:
            logger.warning(
                f"BytePlus requires {artifact_type} URL, not file path. Upload {artifact_type} first."
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
        usage = super()._parse_usage(response_data)
        return VideoGenerationUsage(**usage)

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[VideoGenerationParameters],
    ) -> VideoArtifact:
        """Parse content from response."""
        content = response_data.get("content")
        if not isinstance(content, dict):
            msg = f"No content field in BytePlus response. Available keys: {list(response_data.keys())}"
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


__all__ = ["BytePlusVideoGenerationClient"]
