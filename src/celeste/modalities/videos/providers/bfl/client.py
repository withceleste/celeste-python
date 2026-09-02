"""BFL videos client."""

from typing import Any

from celeste.artifacts import VideoArtifact
from celeste.exceptions import ValidationError
from celeste.mime_types import VideoMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.bfl.utils import encode_artifact
from celeste.providers.bfl.videos import config
from celeste.providers.bfl.videos.client import BFLVideosClient as BFLVideosMixin
from celeste.types import VideoContent

from ...client import VideosClient
from ...io import VideoDraftCache, VideoFinishReason, VideoInput
from .parameters import BFL_PARAMETER_MAPPERS


class BFLVideosClient(BFLVideosMixin, VideosClient):
    """BFL client for FLUX 3 video generation and draft enhancement."""

    _generate_endpoint = config.BFLVideosEndpoint.CREATE_VIDEO
    _enhance_endpoint = config.BFLVideosEndpoint.CREATE_VIDEO

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[VideoContent]]:
        return BFL_PARAMETER_MAPPERS

    def _init_request(self, inputs: VideoInput) -> dict[str, Any]:
        """Build a mode-discriminated FLUX 3 request."""
        if inputs.draft_cache is not None:
            return {
                "mode": "draft_enhance",
                "draft_cache": encode_artifact(inputs.draft_cache),
            }
        if inputs.prompt is None:
            msg = "FLUX 3 video generation requires a prompt"
            raise ValidationError(msg)
        return {"mode": "t2v", "prompt": inputs.prompt}

    def _parse_content(self, response_data: dict[str, Any]) -> VideoArtifact:
        """Parse the signed MP4 URL from a ready BFL result."""
        result = super()._parse_content(response_data)
        sample_url = result.get("sample")
        if not sample_url:
            msg = f"No video URL in {self.provider} response"
            raise ValueError(msg)
        return VideoArtifact(url=sample_url, mime_type=VideoMimeType.MP4)

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Lift reusable draft state into typed video output metadata."""
        metadata = super()._build_metadata(response_data)
        result = response_data.get("result")
        if isinstance(result, dict):
            draft_cache = result.get("draft_cache")
            if isinstance(draft_cache, str) and draft_cache:
                metadata["draft_cache"] = VideoDraftCache(url=draft_cache)
        return metadata

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> VideoFinishReason:
        """Map a ready BFL task to the unified completion reason."""
        return VideoFinishReason(reason="COMPLETE")


__all__ = ["BFLVideosClient"]
