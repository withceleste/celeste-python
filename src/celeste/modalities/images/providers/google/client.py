"""Google images client (Interactions or Vertex selected by auth)."""

from typing import ClassVar

from celeste.client import Forward
from celeste.parameters import ParameterMapper
from celeste.providers.google.auth import GoogleADC
from celeste.providers.google.interactions.config import BASE_URL
from celeste.types import ImageContent

from ...client import ImagesClient
from .interactions import GoogleInteractionsImagesClient
from .models import MODELS
from .parameters import (
    GOOGLE_INTERACTIONS_PARAMETER_MAPPERS,
    GOOGLE_VERTEX_PARAMETER_MAPPERS,
)
from .vertex import GoogleVertexImagesClient

_MODEL_IDS = frozenset(m.id for m in MODELS)


class GoogleImagesClient(ImagesClient):
    """Google images client (selects the Interactions or Vertex backend)."""

    _default_base_url: ClassVar[str] = BASE_URL
    _strategy: GoogleInteractionsImagesClient | GoogleVertexImagesClient | None = None

    def model_post_init(self, __context: object) -> None:
        """Initialize the backend client based on model id and auth type."""
        super().model_post_init(__context)

        if self.model.id not in _MODEL_IDS:
            msg = f"Unknown Google images model: {self.model.id}"
            raise ValueError(msg)

        StrategyClass = (
            GoogleVertexImagesClient
            if isinstance(self.auth, GoogleADC)
            else GoogleInteractionsImagesClient
        )
        strategy = StrategyClass(
            modality=self.modality,
            model=self.model,
            provider=self.provider,
            auth=self.auth,
            base_url=self.base_url,
        )
        object.__setattr__(self, "_strategy", strategy)

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
        return [
            *GOOGLE_INTERACTIONS_PARAMETER_MAPPERS,
            *GOOGLE_VERTEX_PARAMETER_MAPPERS,
        ]

    _generate_endpoint = Forward()
    _edit_endpoint = Forward()
    _upscale_endpoint = Forward()
    _build_url = Forward()
    _init_request = Forward()
    _build_request = Forward()
    _transform_output = Forward()
    _build_metadata = Forward()
    _parse_usage = Forward()
    _parse_content = Forward()
    _parse_finish_reason = Forward()
    _make_request = Forward()


__all__ = ["GoogleImagesClient"]
