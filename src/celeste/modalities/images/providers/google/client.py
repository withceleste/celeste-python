"""Google images client (Interactions or Vertex selected by auth)."""

from typing import Any, ClassVar

from celeste.providers.google.auth import GoogleADC
from celeste.providers.google.interactions.config import BASE_URL

from ...client import ImagesClient
from .interactions import GoogleInteractionsImagesClient
from .models import MODELS
from .vertex import GoogleVertexImagesClient

_MODEL_IDS = frozenset(m.id for m in MODELS)


class GoogleImagesClient(ImagesClient):
    """Google images client: constructing it returns the Vertex backend for GoogleADC auth, else Interactions."""

    _default_base_url: ClassVar[str] = BASE_URL

    def __new__(cls, **data: Any) -> Any:
        if data["model"].id not in _MODEL_IDS:
            msg = f"Unknown Google images model: {data['model'].id}"
            raise ValueError(msg)
        if isinstance(data["auth"], GoogleADC):
            return GoogleVertexImagesClient(**data)
        return GoogleInteractionsImagesClient(**data)


__all__ = ["GoogleImagesClient"]
