"""xAI videos client."""

from typing import Any

from celeste.artifacts import VideoArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.xai.videos import config
from celeste.providers.xai.videos.client import XAIVideosClient as XAIVideosMixin
from celeste.types import VideoContent

from ...client import VideosClient
from ...io import VideoInput
from .parameters import XAI_PARAMETER_MAPPERS


class XAIVideosClient(XAIVideosMixin, VideosClient):
    """xAI client for video generation."""

    _generate_endpoint = config.XAIVideosEndpoint.CREATE_VIDEO
    _edit_endpoint = config.XAIVideosEndpoint.CREATE_EDIT

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[VideoContent]]:
        return XAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: VideoInput) -> dict[str, Any]:
        """Initialize request from inputs."""
        request: dict[str, Any] = {"prompt": inputs.prompt}
        if inputs.video is not None:
            request["video"] = {"url": inputs.video.url}
        return request

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> VideoArtifact:
        """Parse content from response."""
        # xAI returns video URL directly
        url = super()._parse_content(response_data)
        return VideoArtifact(url=url)


__all__ = ["XAIVideosClient"]
