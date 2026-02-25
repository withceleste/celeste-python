"""OpenAI videos client."""

from typing import Any, Unpack

from celeste.artifacts import VideoArtifact
from celeste.mime_types import VideoMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.openai.videos import config
from celeste.providers.openai.videos.client import (
    OpenAIVideosClient as OpenAIVideosMixin,
)
from celeste.types import VideoContent

from ...client import VideosClient
from ...io import VideoInput, VideoOutput
from ...parameters import VideoParameters
from .parameters import OPENAI_PARAMETER_MAPPERS


class OpenAIVideosClient(OpenAIVideosMixin, VideosClient):
    """OpenAI client for video generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[VideoContent]]:
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

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[VideoParameters],
    ) -> VideoArtifact:
        """Parse content from response."""
        video_data_b64 = super()._parse_content(response_data)
        return VideoArtifact(
            data=video_data_b64,
            mime_type=VideoMimeType.MP4,
        )


__all__ = ["OpenAIVideosClient"]
