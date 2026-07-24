"""Google images client (Imagen by model; Gemini models use Interactions or Vertex by auth)."""

from typing import Any, Unpack

from celeste.parameters import ParameterMapper
from celeste.providers.google.auth import GoogleADC
from celeste.types import ImageContent

from ...client import ImagesClient
from ...io import ImageFinishReason, ImageInput
from ...parameters import ImageParameters
from .imagen import GoogleImagenImagesClient
from .interactions import GoogleInteractionsImagesClient
from .models import GOOGLE_GEMINI_MODELS, GOOGLE_IMAGEN_MODELS
from .parameters import (
    GOOGLE_IMAGEN_PARAMETER_MAPPERS,
    GOOGLE_INTERACTIONS_PARAMETER_MAPPERS,
    GOOGLE_VERTEX_PARAMETER_MAPPERS,
)
from .vertex import GoogleVertexImagesClient

_IMAGEN_MODEL_IDS = frozenset(m.id for m in GOOGLE_IMAGEN_MODELS)
_GEMINI_MODEL_IDS = frozenset(m.id for m in GOOGLE_GEMINI_MODELS)


class GoogleImagesClient(ImagesClient):
    """Google images client (selects the Imagen, Interactions, or Vertex backend)."""

    _strategy: (
        GoogleImagenImagesClient
        | GoogleInteractionsImagesClient
        | GoogleVertexImagesClient
        | None
    ) = None

    def model_post_init(self, __context: object) -> None:
        """Initialize the backend client based on model id and auth type."""
        super().model_post_init(__context)

        StrategyClass: type[ImagesClient]
        if self.model.id in _IMAGEN_MODEL_IDS:
            StrategyClass = GoogleImagenImagesClient
        elif self.model.id in _GEMINI_MODEL_IDS:
            StrategyClass = (
                GoogleVertexImagesClient
                if isinstance(self.auth, GoogleADC)
                else GoogleInteractionsImagesClient
            )
        else:
            msg = f"Unknown Google images model: {self.model.id}"
            raise ValueError(msg)

        strategy = StrategyClass(
            modality=self.modality,
            model=self.model,
            provider=self.provider,
            auth=self.auth,
            base_url=self.base_url,
        )
        object.__setattr__(self, "_strategy", strategy)

        if strategy._generate_endpoint is not None:
            object.__setattr__(self, "_generate_endpoint", strategy._generate_endpoint)
        if strategy._edit_endpoint is not None:
            object.__setattr__(self, "_edit_endpoint", strategy._edit_endpoint)
        if strategy._upscale_endpoint is not None:
            object.__setattr__(self, "_upscale_endpoint", strategy._upscale_endpoint)

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
        return [
            *GOOGLE_INTERACTIONS_PARAMETER_MAPPERS,
            *GOOGLE_VERTEX_PARAMETER_MAPPERS,
            *GOOGLE_IMAGEN_PARAMETER_MAPPERS,
        ]

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        return self._strategy._init_request(inputs)  # type: ignore[union-attr]

    def _build_request(
        self,
        inputs: ImageInput,
        **parameters: Unpack[ImageParameters],
    ) -> dict[str, Any]:
        return self._strategy._build_request(inputs, **parameters)  # type: ignore[union-attr]

    def _transform_output(
        self, content: ImageContent, **parameters: Unpack[ImageParameters]
    ) -> ImageContent:
        return self._strategy._transform_output(content, **parameters)  # type: ignore[union-attr]

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        return self._strategy._build_metadata(response_data)  # type: ignore[union-attr]

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        return self._strategy._parse_usage(response_data)  # type: ignore[union-attr]

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> ImageContent:
        return self._strategy._parse_content(response_data)  # type: ignore[union-attr]

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> ImageFinishReason:
        return self._strategy._parse_finish_reason(response_data)  # type: ignore[union-attr]

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[ImageParameters],
    ) -> dict[str, Any]:
        return await self._strategy._make_request(  # type: ignore[union-attr]
            request_body,
            endpoint=endpoint,
            extra_headers=extra_headers,
            **parameters,
        )


__all__ = ["GoogleImagesClient"]
