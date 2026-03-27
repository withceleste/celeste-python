"""Google embeddings client."""

import base64
from typing import Any

from celeste.artifacts import ImageArtifact, VideoArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.google.embeddings.client import (
    GoogleEmbeddingsClient as GoogleEmbeddingsMixin,
)
from celeste.types import EmbeddingsContent
from celeste.utils import detect_mime_type

from ...client import EmbeddingsClient
from ...io import EmbeddingsInput
from .parameters import GOOGLE_PARAMETER_MAPPERS


class GoogleEmbeddingsClient(GoogleEmbeddingsMixin, EmbeddingsClient):
    """Google embeddings client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[EmbeddingsContent]]:
        """Return parameter mappers for Google embeddings."""
        return GOOGLE_PARAMETER_MAPPERS

    def _build_image_part(self, image: ImageArtifact) -> dict[str, Any]:
        """Build a Gemini part from an ImageArtifact."""
        if image.url:
            return {"file_data": {"file_uri": image.url}}
        image_bytes = image.get_bytes()
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        mime = image.mime_type or detect_mime_type(image_bytes)
        mime_str = mime.value if mime else None
        return {"inline_data": {"mime_type": mime_str, "data": b64}}

    def _build_video_part(self, video: VideoArtifact) -> dict[str, Any]:
        """Build a Gemini part from a VideoArtifact."""
        if video.url:
            return {"file_data": {"file_uri": video.url}}
        video_bytes = video.get_bytes()
        b64 = base64.b64encode(video_bytes).decode("utf-8")
        mime = video.mime_type or detect_mime_type(video_bytes)
        mime_str = mime.value if mime else None
        return {"inline_data": {"mime_type": mime_str, "data": b64}}

    def _init_request(self, inputs: EmbeddingsInput) -> dict[str, Any]:
        """Build Google embeddings request from inputs."""
        # Batch images → separate embeddings via batchEmbedContents
        if isinstance(inputs.images, list):
            return {
                "requests": [
                    {
                        "model": f"models/{self.model.id}",
                        "content": {"parts": [self._build_image_part(img)]},
                    }
                    for img in inputs.images
                ]
            }

        # Batch videos → separate embeddings via batchEmbedContents
        if isinstance(inputs.videos, list):
            return {
                "requests": [
                    {
                        "model": f"models/{self.model.id}",
                        "content": {"parts": [self._build_video_part(vid)]},
                    }
                    for vid in inputs.videos
                ]
            }

        # Single/combined multimodal → one aggregated embedding
        if inputs.images is not None or inputs.videos is not None:
            parts: list[dict[str, Any]] = []
            if inputs.text is not None:
                parts.append({"text": inputs.text})
            if inputs.images is not None:
                parts.append(self._build_image_part(inputs.images))
            if inputs.videos is not None:
                parts.append(self._build_video_part(inputs.videos))
            return {"content": {"parts": parts}}

        # Text-only (existing behavior)
        assert inputs.text is not None
        texts = inputs.text if isinstance(inputs.text, list) else [inputs.text]
        if len(texts) == 1:
            return {"content": {"parts": [{"text": texts[0]}]}}
        return {
            "requests": [
                {
                    "model": f"models/{self.model.id}",
                    "content": {"parts": [{"text": text}]},
                }
                for text in texts
            ]
        }

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> EmbeddingsContent:
        """Parse embedding vectors from response."""
        return super()._parse_content(response_data)


__all__ = ["GoogleEmbeddingsClient"]
