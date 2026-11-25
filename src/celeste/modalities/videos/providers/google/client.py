"""Google videos client (Veo by model family; Omni models use Interactions)."""

from typing import ClassVar

from celeste.client import Forward
from celeste.parameters import ParameterMapper
from celeste.providers.google.interactions.config import BASE_URL
from celeste.types import VideoContent

from ...client import VideosClient
from .interactions import GoogleInteractionsVideosClient
from .models import GOOGLE_OMNI_MODELS, GOOGLE_VEO_MODELS
from .parameters import (
    GOOGLE_INTERACTIONS_PARAMETER_MAPPERS,
    GOOGLE_VEO_PARAMETER_MAPPERS,
)
from .veo import GoogleVeoVideosClient

_VEO_MODEL_IDS = frozenset(m.id for m in GOOGLE_VEO_MODELS)
_OMNI_MODEL_IDS = frozenset(m.id for m in GOOGLE_OMNI_MODELS)


class GoogleVideosClient(VideosClient):
    """Google videos client (selects the Veo or Interactions backend by model id)."""

    _default_base_url: ClassVar[str] = BASE_URL
    _strategy: GoogleVeoVideosClient | GoogleInteractionsVideosClient | None = None

    def model_post_init(self, __context: object) -> None:
        """Initialize the backend client based on model id."""
        super().model_post_init(__context)

        StrategyClass: type[VideosClient]
        if self.model.id in _VEO_MODEL_IDS:
            StrategyClass = GoogleVeoVideosClient
        elif self.model.id in _OMNI_MODEL_IDS:
            StrategyClass = GoogleInteractionsVideosClient
        else:
            msg = f"Unknown Google videos model: {self.model.id}"
            raise ValueError(msg)

        strategy = StrategyClass(
            modality=self.modality,
            model=self.model,
            provider=self.provider,
            auth=self.auth,
            base_url=self.base_url,
        )
        object.__setattr__(self, "_strategy", strategy)

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[VideoContent]]:
        return [
            *GOOGLE_VEO_PARAMETER_MAPPERS,
            *GOOGLE_INTERACTIONS_PARAMETER_MAPPERS,
        ]

    _generate_endpoint = Forward()
    _edit_endpoint = Forward()
    _build_url = Forward()
    _init_request = Forward()
    _build_request = Forward()
    _transform_output = Forward()
    _build_metadata = Forward()
    _parse_usage = Forward()
    _parse_content = Forward()
    _parse_finish_reason = Forward()
    _make_request = Forward()
    download_content = Forward()


__all__ = ["GoogleVideosClient"]
