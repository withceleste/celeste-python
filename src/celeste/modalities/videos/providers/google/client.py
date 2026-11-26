"""Google videos client (Veo by model family; Omni models use Interactions)."""

from typing import Any, ClassVar

from celeste.providers.google.interactions.config import BASE_URL

from ...client import VideosClient
from .interactions import GoogleInteractionsVideosClient
from .models import GOOGLE_OMNI_MODELS, GOOGLE_VEO_MODELS
from .veo import GoogleVeoVideosClient

_VEO_MODEL_IDS = frozenset(m.id for m in GOOGLE_VEO_MODELS)
_OMNI_MODEL_IDS = frozenset(m.id for m in GOOGLE_OMNI_MODELS)


class GoogleVideosClient(VideosClient):
    """Google videos client: constructing it returns the Veo or Interactions backend by model id."""

    _default_base_url: ClassVar[str] = BASE_URL

    def __new__(cls, **data: Any) -> Any:
        model_id = data["model"].id
        if model_id in _VEO_MODEL_IDS:
            return GoogleVeoVideosClient(**data)
        if model_id in _OMNI_MODEL_IDS:
            return GoogleInteractionsVideosClient(**data)
        msg = f"Unknown Google videos model: {model_id}"
        raise ValueError(msg)


__all__ = ["GoogleVideosClient"]
