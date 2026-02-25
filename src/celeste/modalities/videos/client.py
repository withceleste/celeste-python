"""Videos modality client."""

from typing import Any, Unpack

from asgiref.sync import async_to_sync

from celeste.client import ModalityClient
from celeste.core import Modality
from celeste.types import VideoContent

from .io import VideoFinishReason, VideoInput, VideoOutput, VideoUsage
from .parameters import VideoParameters


class VideosClient(
    ModalityClient[VideoInput, VideoOutput, VideoParameters, VideoContent]
):
    """Base videos client. Providers implement generate method."""

    modality: Modality = Modality.VIDEOS
    _usage_class = VideoUsage
    _finish_reason_class = VideoFinishReason

    @classmethod
    def _output_class(cls) -> type[VideoOutput]:
        """Return the Output class for videos modality."""
        return VideoOutput

    @property
    def sync(self) -> "VideosSyncNamespace":
        """Sync namespace for videos operations."""
        return VideosSyncNamespace(self)


class VideosSyncNamespace:
    """Sync namespace for videos operations.

    Provides `client.sync.generate()`.
    """

    def __init__(self, client: VideosClient) -> None:
        self._client = client

    def generate(
        self,
        prompt: str,
        *,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[VideoParameters],
    ) -> VideoOutput:
        """Blocking video generation.

        Usage:
            result = client.sync.generate("A cat walking on the beach")
            result.content.save("video.mp4")
        """
        inputs = VideoInput(prompt=prompt)
        return async_to_sync(self._client._predict)(
            inputs, extra_body=extra_body, extra_headers=extra_headers, **parameters
        )


__all__ = [
    "VideosClient",
    "VideosSyncNamespace",
]
