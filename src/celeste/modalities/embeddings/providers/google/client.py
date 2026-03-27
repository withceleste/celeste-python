"""Google embeddings client."""

from typing import Any

from celeste.parameters import ParameterMapper
from celeste.providers.google.embeddings.client import (
    GoogleEmbeddingsClient as GoogleEmbeddingsMixin,
)
from celeste.providers.google.utils import build_media_part
from celeste.types import EmbeddingsContent

from ...client import EmbeddingsClient
from ...io import EmbeddingsInput
from .parameters import GOOGLE_PARAMETER_MAPPERS


class GoogleEmbeddingsClient(GoogleEmbeddingsMixin, EmbeddingsClient):
    """Google embeddings client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[EmbeddingsContent]]:
        """Return parameter mappers for Google embeddings."""
        return GOOGLE_PARAMETER_MAPPERS

    def _init_request(self, inputs: EmbeddingsInput) -> dict[str, Any]:
        """Build Google embeddings request from inputs."""
        # Batch media → separate embeddings via batchEmbedContents
        for field in (inputs.images, inputs.videos, inputs.audio):
            if isinstance(field, list):
                return {
                    "requests": [
                        {
                            "model": f"models/{self.model.id}",
                            "content": {"parts": [build_media_part(item)]},
                        }
                        for item in field
                    ]
                }

        # Single/combined multimodal → one aggregated embedding
        media = [
            f
            for f in (inputs.images, inputs.videos, inputs.audio)
            if f is not None and not isinstance(f, list)
        ]
        if media:
            parts: list[dict[str, Any]] = []
            if inputs.text is not None:
                parts.append({"text": inputs.text})
            for artifact in media:
                parts.append(build_media_part(artifact))
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
