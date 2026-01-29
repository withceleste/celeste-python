"""xAI videos client."""

from typing import Any, Unpack

from celeste.artifacts import VideoArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.xai.videos import config
from celeste.providers.xai.videos.client import XAIVideosClient as XAIVideosMixin

from ...client import VideosClient
from ...io import VideoFinishReason, VideoInput, VideoOutput, VideoUsage
from ...parameters import VideoParameters
from .parameters import XAI_PARAMETER_MAPPERS


class XAIVideosClient(XAIVideosMixin, VideosClient):
    """xAI client for video generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return XAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: VideoInput) -> dict[str, Any]:
        """Initialize request from inputs."""
        request: dict[str, Any] = {"prompt": inputs.prompt}
        if inputs.video is not None:
            request["video"] = {"url": inputs.video.url}
        return request

    async def generate(
        self,
        prompt: str,
        **parameters: Unpack[VideoParameters],
    ) -> VideoOutput:
        """Generate videos from prompt."""
        inputs = VideoInput(prompt=prompt)
        return await self._predict(
            inputs,
            endpoint=config.XAIVideosEndpoint.CREATE_VIDEO,
            **parameters,
        )

    async def edit(
        self,
        video: VideoArtifact,
        prompt: str,
        **parameters: Unpack[VideoParameters],
    ) -> VideoOutput:
        """Edit a video with text instructions."""
        inputs = VideoInput(prompt=prompt, video=video)
        return await self._predict(
            inputs,
            endpoint=config.XAIVideosEndpoint.CREATE_EDIT,
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
        # xAI returns video URL directly
        url = super()._parse_content(response_data)
        return VideoArtifact(url=url)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> VideoFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return VideoFinishReason(reason=finish_reason.reason)


__all__ = ["XAIVideosClient"]
