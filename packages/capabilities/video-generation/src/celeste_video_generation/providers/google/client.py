"""Google client implementation for video generation."""

from typing import Any, Unpack

from celeste_google.veo.client import GoogleVeoClient

from celeste.artifacts import VideoArtifact
from celeste.mime_types import VideoMimeType
from celeste.parameters import ParameterMapper
from celeste_video_generation.client import VideoGenerationClient
from celeste_video_generation.io import (
    VideoGenerationInput,
    VideoGenerationUsage,
)
from celeste_video_generation.parameters import VideoGenerationParameters

from .parameters import GOOGLE_PARAMETER_MAPPERS


class GoogleVideoGenerationClient(GoogleVeoClient, VideoGenerationClient):
    """Google client for video generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return GOOGLE_PARAMETER_MAPPERS

    def _init_request(self, inputs: VideoGenerationInput) -> dict[str, Any]:
        """Initialize request from Google API format."""
        instance: dict[str, Any] = {"prompt": inputs.prompt}

        request: dict[str, Any] = {"instances": [instance]}
        request["parameters"] = {}

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
        video_data = super()._parse_content(response_data)
        uri = video_data.get("uri")
        if not uri:
            msg = "No video URI in response"
            raise ValueError(msg)

        video_artifact = VideoArtifact(url=uri)

        transformed = self._transform_output(video_artifact, **parameters)
        if isinstance(transformed, VideoArtifact):
            return transformed
        return video_artifact

    async def download_content(self, artifact: VideoArtifact) -> VideoArtifact:
        """Download video content from URI."""
        if not artifact.url:
            msg = "VideoArtifact has no URL to download from"
            raise ValueError(msg)

        video_bytes = await super().download_content(artifact.url)

        return VideoArtifact(
            url=artifact.url,
            data=video_bytes,
            mime_type=VideoMimeType.MP4,
            metadata=artifact.metadata,
        )


__all__ = ["GoogleVideoGenerationClient"]
