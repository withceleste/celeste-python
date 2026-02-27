"""Google videos client."""

from typing import Any, Unpack

from celeste.artifacts import VideoArtifact
from celeste.mime_types import VideoMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.google.veo import config
from celeste.providers.google.veo.client import GoogleVeoClient as GoogleVeoMixin
from celeste.types import VideoContent

from ...client import VideosClient
from ...io import VideoInput, VideoOutput
from ...parameters import VideoParameters
from .parameters import GOOGLE_PARAMETER_MAPPERS


class GoogleVideosClient(GoogleVeoMixin, VideosClient):
    """Google client for video generation."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[VideoContent]]:
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

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> VideoArtifact:
        """Parse content from response."""
        video_data = super()._parse_content(response_data)
        # Handle inline base64 response (Vertex can return bytesBase64Encoded)
        if "bytesBase64Encoded" in video_data:
            mime_type = video_data.get("mimeType", VideoMimeType.MP4)
            return VideoArtifact(
                data=video_data["bytesBase64Encoded"], mime_type=mime_type
            )
        return VideoArtifact(url=video_data.get("uri"))

    async def download_content(self, artifact: VideoArtifact) -> VideoArtifact:
        """Download video content from GCS URL.

        Args:
            artifact: VideoArtifact with URL or inline data to download.

        Returns:
            VideoArtifact with downloaded bytes data.
        """
        if artifact.data is not None:
            return artifact

        if artifact.url is None:
            msg = "Artifact has no URL or data to download"
            raise ValueError(msg)

        video_bytes = await super().download_content(artifact.url)
        return VideoArtifact(
            data=video_bytes,
            mime_type=artifact.mime_type,
        )


__all__ = ["GoogleVideosClient"]
