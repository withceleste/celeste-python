"""BytePlus videos client."""

from typing import Any

from celeste.artifacts import VideoArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.byteplus.videos import config
from celeste.providers.byteplus.videos.client import (
    BytePlusVideosClient as BytePlusVideosMixin,
)
from celeste.types import VideoContent

from ...client import VideosClient
from ...io import VideoInput
from .parameters import BYTEPLUS_PARAMETER_MAPPERS


class BytePlusVideosClient(BytePlusVideosMixin, VideosClient):
    """BytePlus client for video generation."""

    _generate_endpoint = config.BytePlusVideosEndpoint.CREATE_VIDEO

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[VideoContent]]:
        return BYTEPLUS_PARAMETER_MAPPERS

    def _init_request(self, inputs: VideoInput) -> dict[str, Any]:
        """Initialize request from BytePlus ModelArk API format."""
        return {
            "content": [{"type": "text", "text": inputs.prompt}],
        }

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> VideoArtifact:
        """Parse content from response."""
        content = super()._parse_content(response_data)
        video_url = content.get("video_url")
        if not video_url:
            msg = "No video_url in response content"
            raise ValueError(msg)
        return VideoArtifact(url=video_url)


__all__ = ["BytePlusVideosClient"]
