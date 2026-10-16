"""BFL videos client."""

from typing import Any

from celeste.artifacts import VideoArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.bfl.flux import config
from celeste.providers.bfl.flux.client import BFLFluxClient as BFLFluxMixin
from celeste.types import VideoContent

from ...client import VideosClient
from ...io import VideoInput
from .parameters import BFL_PARAMETER_MAPPERS


class BFLVideosClient(BFLFluxMixin, VideosClient):
    """BFL client for video generation."""

    _generate_endpoint = config.BFLFluxEndpoint.CREATE_TASK

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[VideoContent]]:
        return BFL_PARAMETER_MAPPERS

    def _init_request(self, inputs: VideoInput) -> dict[str, Any]:
        """Initialize a text-to-video request."""
        return {"mode": "t2v", "prompt": inputs.prompt}

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> VideoArtifact:
        """Parse content from response."""
        result = super()._parse_content(response_data)
        sample_url = result.get("sample")

        if not sample_url:
            msg = f"No video URL in {self.provider} response"
            raise ValueError(msg)

        return VideoArtifact(url=sample_url)


__all__ = ["BFLVideosClient"]
