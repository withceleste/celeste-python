"""BytePlus videos client."""

from typing import Any, Unpack

from celeste.artifacts import VideoArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.byteplus.videos import config
from celeste.providers.byteplus.videos.client import (
    BytePlusVideosClient as BytePlusVideosMixin,
)

from ...client import VideosClient
from ...io import VideoFinishReason, VideoInput, VideoOutput, VideoUsage
from ...parameters import VideoParameters
from .parameters import BYTEPLUS_PARAMETER_MAPPERS


class BytePlusVideosClient(BytePlusVideosMixin, VideosClient):
    """BytePlus client for video generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return BYTEPLUS_PARAMETER_MAPPERS

    def _init_request(self, inputs: VideoInput) -> dict[str, Any]:
        """Initialize request from BytePlus ModelArk API format."""
        return {
            "content": [{"type": "text", "text": inputs.prompt}],
        }

    async def generate(
        self,
        prompt: str,
        **parameters: Unpack[VideoParameters],
    ) -> VideoOutput:
        """Generate videos from prompt."""
        inputs = VideoInput(prompt=prompt)
        return await self._predict(
            inputs,
            endpoint=config.BytePlusVideosEndpoint.CREATE_VIDEO,
            **parameters,
        )

    def _parse_usage(self, response_data: dict[str, Any]) -> VideoUsage:
        """Parse usage from response."""
        usage = super()._parse_usage(response_data)
        return VideoUsage(**usage)

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[VideoParameters],
    ) -> VideoArtifact:
        """Parse content from response."""
        content = super()._parse_content(response_data)
        video_url = content.get("video_url")
        if not video_url:
            msg = "No video_url in response content"
            raise ValueError(msg)
        return VideoArtifact(url=video_url)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> VideoFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return VideoFinishReason(reason=finish_reason.reason)


__all__ = ["BytePlusVideosClient"]
