"""BFL images client (FLUX 3, FLUX.2, FLUX.1 Kontext or FLUX.1 by model family)."""

from typing import Any, Unpack

from celeste.parameters import ParameterMapper
from celeste.types import ImageContent

from ...client import ImagesClient
from ...io import ImageFinishReason, ImageInput
from ...parameters import ImageParameters
from .flux1 import BFLFlux1ImagesClient
from .flux2 import BFLFlux2ImagesClient
from .flux3 import BFLFlux3ImagesClient
from .kontext import BFLKontextImagesClient
from .models import (
    BFL_FLUX1_MODELS,
    BFL_FLUX2_MODELS,
    BFL_FLUX3_MODELS,
    BFL_KONTEXT_MODELS,
)
from .parameters import (
    BFL_FLUX1_PARAMETER_MAPPERS,
    BFL_FLUX2_PARAMETER_MAPPERS,
    BFL_FLUX3_PARAMETER_MAPPERS,
    BFL_KONTEXT_PARAMETER_MAPPERS,
)

_FLUX3_MODEL_IDS = frozenset(m.id for m in BFL_FLUX3_MODELS)
_FLUX2_MODEL_IDS = frozenset(m.id for m in BFL_FLUX2_MODELS)
_KONTEXT_MODEL_IDS = frozenset(m.id for m in BFL_KONTEXT_MODELS)
_FLUX1_MODEL_IDS = frozenset(m.id for m in BFL_FLUX1_MODELS)


class BFLImagesClient(ImagesClient):
    """BFL images client (selects the FLUX 3, FLUX.2, FLUX.1 Kontext or FLUX.1 backend)."""

    _strategy: (
        BFLFlux3ImagesClient
        | BFLFlux2ImagesClient
        | BFLKontextImagesClient
        | BFLFlux1ImagesClient
        | None
    ) = None

    def model_post_init(self, __context: object) -> None:
        """Initialize the backend client based on model id."""
        super().model_post_init(__context)

        StrategyClass: type[ImagesClient]
        if self.model.id in _FLUX3_MODEL_IDS:
            StrategyClass = BFLFlux3ImagesClient
        elif self.model.id in _FLUX2_MODEL_IDS:
            StrategyClass = BFLFlux2ImagesClient
        elif self.model.id in _KONTEXT_MODEL_IDS:
            StrategyClass = BFLKontextImagesClient
        elif self.model.id in _FLUX1_MODEL_IDS:
            StrategyClass = BFLFlux1ImagesClient
        else:
            msg = f"Unknown BFL images model: {self.model.id}"
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

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
        return [
            *BFL_FLUX3_PARAMETER_MAPPERS,
            *BFL_FLUX2_PARAMETER_MAPPERS,
            *BFL_KONTEXT_PARAMETER_MAPPERS,
            *BFL_FLUX1_PARAMETER_MAPPERS,
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


__all__ = ["BFLImagesClient"]
