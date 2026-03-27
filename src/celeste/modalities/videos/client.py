"""Videos modality client."""

from typing import Any, ClassVar, Unpack

from asgiref.sync import async_to_sync

from celeste.artifacts import VideoArtifact
from celeste.client import ModalityClient
from celeste.core import Modality
from celeste.types import VideoContent

from .io import VideoChunk, VideoFinishReason, VideoInput, VideoOutput, VideoUsage
from .parameters import VideoParameters


class VideosClient(
    ModalityClient[VideoInput, VideoOutput, VideoParameters, VideoContent, VideoChunk]
):
    """Base videos client with generate/edit operations."""

    modality: Modality = Modality.VIDEOS
    _usage_class = VideoUsage
    _finish_reason_class = VideoFinishReason

    _generate_endpoint: ClassVar[str | None] = None
    _edit_endpoint: ClassVar[str | None] = None

    @classmethod
    def _output_class(cls) -> type[VideoOutput]:
        """Return the Output class for videos modality."""
        return VideoOutput

    async def generate(
        self,
        prompt: str,
        **parameters: Unpack[VideoParameters],
    ) -> VideoOutput:
        """Generate videos from prompt."""
        inputs = VideoInput(prompt=prompt)
        return await self._predict(
            inputs, endpoint=self._generate_endpoint, **parameters
        )

    async def edit(
        self,
        video: VideoArtifact,
        prompt: str,
        **parameters: Unpack[VideoParameters],
    ) -> VideoOutput:
        """Edit a video with text instructions."""
        if self._edit_endpoint is None:
            msg = f"Model {self.model.id} does not support video editing"
            raise NotImplementedError(msg)
        inputs = VideoInput(prompt=prompt, video=video)
        return await self._predict(inputs, endpoint=self._edit_endpoint, **parameters)

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
