"""Google embeddings client."""

from typing import Any, Unpack

from celeste.parameters import ParameterMapper
from celeste.providers.google.embeddings.client import (
    GoogleEmbeddingsClient as GoogleEmbeddingsMixin,
)
from celeste.types import EmbeddingsContent

from ...client import EmbeddingsClient
from ...io import (
    EmbeddingsFinishReason,
    EmbeddingsInput,
    EmbeddingsUsage,
)
from ...parameters import EmbeddingsParameters
from .parameters import GOOGLE_PARAMETER_MAPPERS


class GoogleEmbeddingsClient(GoogleEmbeddingsMixin, EmbeddingsClient):
    """Google embeddings client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        """Return parameter mappers for Google embeddings."""
        return GOOGLE_PARAMETER_MAPPERS

    def _init_request(self, inputs: EmbeddingsInput) -> dict[str, Any]:
        """Build Google embeddings request from inputs."""
        texts = inputs.text if isinstance(inputs.text, list) else [inputs.text]

        if len(texts) == 1:
            return {"content": {"parts": [{"text": texts[0]}]}}
        else:
            return {
                "requests": [
                    {
                        "model": f"models/{self.model.id}",
                        "content": {"parts": [{"text": text}]},
                    }
                    for text in texts
                ]
            }

    def _parse_usage(self, response_data: dict[str, Any]) -> EmbeddingsUsage:
        """Parse usage from response (embeddings API doesn't provide usage)."""
        usage = super()._parse_usage(response_data)
        return EmbeddingsUsage(**usage)

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[EmbeddingsParameters],
    ) -> EmbeddingsContent:
        """Parse embedding vectors from response."""
        return super()._parse_content(response_data)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> EmbeddingsFinishReason:
        """Parse finish reason (embeddings API doesn't provide finish reasons)."""
        finish_reason = super()._parse_finish_reason(response_data)
        return EmbeddingsFinishReason(reason=finish_reason.reason)


__all__ = ["GoogleEmbeddingsClient"]
