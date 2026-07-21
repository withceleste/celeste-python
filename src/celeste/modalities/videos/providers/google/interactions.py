"""Google videos client (Interactions API — Gemini Omni)."""

from typing import Any

from celeste.artifacts import VideoArtifact
from celeste.mime_types import VideoMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.google.interactions import config
from celeste.providers.google.interactions.client import (
    GoogleInteractionsClient as GoogleInteractionsMixin,
)
from celeste.providers.google.utils import build_content_part
from celeste.types import VideoContent

from ...client import VideosClient
from ...io import VideoInput
from .parameters import GOOGLE_INTERACTIONS_PARAMETER_MAPPERS


class GoogleInteractionsVideosClient(GoogleInteractionsMixin, VideosClient):
    """Google videos client (Interactions API)."""

    _generate_endpoint = config.GoogleInteractionsEndpoint.CREATE_INTERACTION
    _edit_endpoint = config.GoogleInteractionsEndpoint.CREATE_INTERACTION

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[VideoContent]]:
        return GOOGLE_INTERACTIONS_PARAMETER_MAPPERS

    def _init_request(self, inputs: VideoInput) -> dict[str, Any]:
        """Initialize request for Omni video generation/edit."""
        request: dict[str, Any] = {"response_format": {"type": "video"}}
        if inputs.video is None:
            request["input"] = inputs.prompt
            return request
        request["input"] = [
            build_content_part(inputs.video, "video"),
            {"type": "text", "text": inputs.prompt},
        ]
        request["generation_config"] = {"video_config": {"task": "edit"}}
        return request

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> VideoArtifact:
        """Parse the video artifact from the model_output step."""
        steps = super()._parse_content(response_data)
        for step in steps:
            if step.get("type") != "model_output":
                continue
            for part in step.get("content", []):
                if part.get("type") != "video":
                    continue
                mime_type = VideoMimeType(part.get("mime_type", "video/mp4"))
                if part.get("data"):
                    return VideoArtifact(data=part["data"], mime_type=mime_type)
                if part.get("uri"):
                    return VideoArtifact(url=part["uri"], mime_type=mime_type)
        msg = "No video content in response"
        raise ValueError(msg)

    async def download_content(self, artifact: VideoArtifact) -> VideoArtifact:
        """Download video content from the response URI."""
        if artifact.data is not None:
            return artifact

        if artifact.url is None:
            msg = "Artifact has no URL or data to download"
            raise ValueError(msg)

        headers = self.auth.get_headers()
        response = await self.http_client.get(
            artifact.url, headers=headers, follow_redirects=True
        )
        self._handle_error_response(response)
        return VideoArtifact(data=response.content, mime_type=artifact.mime_type)


__all__ = ["GoogleInteractionsVideosClient"]
