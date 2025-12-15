"""Google client implementation for image generation."""

from typing import Any, Unpack

import httpx

from celeste.artifacts import ImageArtifact
from celeste.parameters import ParameterMapper
from celeste_image_generation.client import ImageGenerationClient
from celeste_image_generation.io import (
    ImageGenerationFinishReason,
    ImageGenerationInput,
    ImageGenerationUsage,
)
from celeste_image_generation.parameters import ImageGenerationParameters

from .gemini import GeminiImageGenerationClient
from .imagen import ImagenImageGenerationClient
from .models import GEMINI_MODELS, IMAGEN_MODELS
from .parameters import GOOGLE_PARAMETER_MAPPERS

# Model ID → Client class mapping (extensible - add new model types here)
GOOGLE_MODEL_MAP = {
    **{m.id: ImagenImageGenerationClient for m in IMAGEN_MODELS},
    **{m.id: GeminiImageGenerationClient for m in GEMINI_MODELS},
}


class GoogleImageGenerationClient(ImageGenerationClient):
    """Google client for image generation."""

    _strategy: GeminiImageGenerationClient | ImagenImageGenerationClient | None = None

    def model_post_init(self, __context: object) -> None:
        """Initialize strategy based on model."""
        super().model_post_init(__context)

        StrategyClass = GOOGLE_MODEL_MAP[self.model.id]
        strategy = StrategyClass(
            model=self.model,
            provider=self.provider,
            capability=self.capability,
            auth=self.auth,
        )
        object.__setattr__(self, "_strategy", strategy)

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return GOOGLE_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageGenerationInput) -> dict[str, Any]:
        """Delegate to strategy."""
        return self._strategy._init_request(inputs)  # type: ignore[union-attr]

    def _parse_usage(self, response_data: dict[str, Any]) -> ImageGenerationUsage:
        """Delegate to strategy."""
        return self._strategy._parse_usage(response_data)  # type: ignore[union-attr]

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> ImageArtifact | list[ImageArtifact]:
        """Delegate to strategy."""
        return self._strategy._parse_content(response_data, **parameters)  # type: ignore[union-attr]

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> ImageGenerationFinishReason:
        """Delegate to strategy."""
        return self._strategy._parse_finish_reason(response_data)  # type: ignore[union-attr]

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> httpx.Response:
        """Delegate to strategy."""
        return await self._strategy._make_request(request_body, **parameters)  # type: ignore[union-attr]


__all__ = ["GoogleImageGenerationClient"]
