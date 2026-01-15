"""Google videos client."""

from typing import Any, Unpack

from celeste.artifacts import VideoArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.google.veo import config
from celeste.providers.google.veo.client import GoogleVeoClient as GoogleVeoMixin

from ...client import VideosClient
from ...io import VideoFinishReason, VideoInput, VideoOutput, VideoUsage
from ...parameters import VideoParameters
from .parameters import GOOGLE_PARAMETER_MAPPERS


class GoogleVideosClient(GoogleVeoMixin, VideosClient):
    """Google client for video generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return GOOGLE_PARAMETER_MAPPERS

    def _init_request(self, inputs: VideoInput) -> dict[str, Any]:
        """Initialize request from Google Veo API format."""
        return {
            "instances": [{"prompt": inputs.prompt}],
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
            endpoint=config.GoogleVeoEndpoint.CREATE_VIDEO,
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
        video_data = super()._parse_content(response_data)
        return VideoArtifact(url=video_data.get("uri"))

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> VideoFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return VideoFinishReason(reason=finish_reason.reason)

    async def download_content(self, artifact: VideoArtifact) -> VideoArtifact:
        """Download video content from GCS URL.

        Args:
            artifact: VideoArtifact with URL to download.

        Returns:
            VideoArtifact with downloaded bytes data.
        """
        if artifact.url is None:
            msg = "Artifact has no URL to download"
            raise ValueError(msg)

        video_bytes = await super().download_content(artifact.url)
        return VideoArtifact(
            data=video_bytes,
            mime_type=artifact.mime_type,
        )


__all__ = ["GoogleVideosClient"]
