"""Google text client (Interactions API; GoogleADC auth uses Vertex GenerateContent)."""

from typing import Any, ClassVar

from celeste.providers.google.auth import GoogleADC
from celeste.providers.google.interactions.config import BASE_URL

from ...client import TextClient
from .interactions import GoogleInteractionsTextClient
from .vertex import GoogleVertexTextClient


class GoogleTextClient(TextClient):
    """Google text client: constructing it returns the Vertex backend for GoogleADC auth, else Interactions."""

    _default_base_url: ClassVar[str] = BASE_URL

    def __new__(cls, **data: Any) -> Any:
        if isinstance(data["auth"], GoogleADC):
            return GoogleVertexTextClient(**data)
        return GoogleInteractionsTextClient(**data)


__all__ = ["GoogleTextClient"]
