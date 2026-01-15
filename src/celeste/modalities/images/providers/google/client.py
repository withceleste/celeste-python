"""Google images client."""

from typing import Any, Unpack

from celeste.artifacts import ImageArtifact
from celeste.parameters import ParameterMapper
from celeste.types import ImageContent

from ...client import ImagesClient
from ...io import ImageFinishReason, ImageInput, ImageOutput, ImageUsage
from ...parameters import ImageParameters
from .gemini import GeminiImagesClient
from .imagen import ImagenImagesClient
from .models import GEMINI_MODELS, IMAGEN_MODELS
from .parameters import GEMINI_PARAMETER_MAPPERS, IMAGEN_PARAMETER_MAPPERS

# Model ID → Strategy class mapping
GOOGLE_MODEL_MAP: dict[str, type[GeminiImagesClient] | type[ImagenImagesClient]] = {
    **{m.id: ImagenImagesClient for m in IMAGEN_MODELS},
    **{m.id: GeminiImagesClient for m in GEMINI_MODELS},
}


class GoogleImagesClient(ImagesClient):
    """Google images client (dispatches between Imagen and Gemini backends)."""

    _strategy: GeminiImagesClient | ImagenImagesClient | None = None

    def model_post_init(self, __context: object) -> None:
        """Initialize strategy based on model id."""
        super().model_post_init(__context)

        StrategyClass = GOOGLE_MODEL_MAP.get(self.model.id)
        if StrategyClass is None:
            msg = f"Unknown Google images model: {self.model.id}"
            raise ValueError(msg)

        strategy = StrategyClass(
            modality=self.modality,
            model=self.model,
            provider=self.provider,
            auth=self.auth,
        )
        object.__setattr__(self, "_strategy", strategy)

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return [*GEMINI_PARAMETER_MAPPERS, *IMAGEN_PARAMETER_MAPPERS]

    async def generate(
        self,
        prompt: str,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Generate images from prompt."""
        inputs = ImageInput(prompt=prompt)
        return await self._predict(inputs, **parameters)

    async def edit(
        self,
        image: ImageArtifact,
        prompt: str,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        # Only Gemini supports edit in Google provider
        if not isinstance(self._strategy, GeminiImagesClient):
            msg = f"Model '{self.model.id}' does not support image editing"
            raise ValueError(msg)

        inputs = ImageInput(prompt=prompt, image=image)
        return await self._predict(inputs, **parameters)

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Delegate to strategy's _init_request."""
        return self._strategy._init_request(inputs)  # type: ignore[union-attr]

    def _build_request(
        self,
        inputs: ImageInput,
        **parameters: Unpack[ImageParameters],
    ) -> dict[str, Any]:
        return self._strategy._build_request(inputs, **parameters)  # type: ignore[union-attr]

    def _parse_usage(self, response_data: dict[str, Any]) -> ImageUsage:
        return self._strategy._parse_usage(response_data)  # type: ignore[union-attr]

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageParameters],
    ) -> ImageContent:
        return self._strategy._parse_content(response_data, **parameters)  # type: ignore[union-attr]

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> ImageFinishReason:
        return self._strategy._parse_finish_reason(response_data)  # type: ignore[union-attr]

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Unpack[ImageParameters],
    ) -> dict[str, Any]:
        return await self._strategy._make_request(  # type: ignore[union-attr]
            request_body,
            endpoint=endpoint,
            **parameters,
        )


__all__ = ["GoogleImagesClient"]
