"""OpenAI videos client."""

import base64
from typing import Any, Unpack

from celeste.artifacts import VideoArtifact
from celeste.mime_types import VideoMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.openai.videos import config
from celeste.providers.openai.videos.client import (
    OpenAIVideosClient as OpenAIVideosMixin,
)

from ...client import VideosClient
from ...io import VideoFinishReason, VideoInput, VideoOutput, VideoUsage
from ...parameters import VideoParameters
from .parameters import OPENAI_PARAMETER_MAPPERS


class OpenAIVideosClient(OpenAIVideosMixin, VideosClient):
    """OpenAI client for video generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return OPENAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: VideoInput) -> dict[str, Any]:
        """Initialize request from OpenAI API format."""
        return {
            "prompt": inputs.prompt,
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
            endpoint=config.OpenAIVideosEndpoint.CREATE_VIDEO,
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
        video_data_b64 = super()._parse_content(response_data)
        video_data = base64.b64decode(video_data_b64)
        return VideoArtifact(
            data=video_data,
            mime_type=VideoMimeType.MP4,
        )

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> VideoFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return VideoFinishReason(reason=finish_reason.reason)


__all__ = ["OpenAIVideosClient"]
