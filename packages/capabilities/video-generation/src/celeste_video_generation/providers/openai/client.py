"""OpenAI client implementation for video generation."""

import base64
import io
import json
from typing import Any, Unpack

from celeste_openai.videos.client import OpenAIVideosClient
from PIL import Image

from celeste.artifacts import ImageArtifact, VideoArtifact
from celeste.exceptions import ValidationError
from celeste.mime_types import VideoMimeType
from celeste.parameters import ParameterMapper
from celeste_video_generation.client import VideoGenerationClient
from celeste_video_generation.io import (
    VideoGenerationInput,
    VideoGenerationUsage,
)
from celeste_video_generation.parameters import VideoGenerationParameters

from .parameters import OPENAI_PARAMETER_MAPPERS


class OpenAIVideoGenerationClient(OpenAIVideosClient, VideoGenerationClient):
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
        usage = super()._parse_usage(response_data)
        return VideoGenerationUsage(**usage)

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


__all__ = ["OpenAIVideoGenerationClient"]
