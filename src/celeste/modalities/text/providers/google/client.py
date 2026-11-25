"""Google text client (Interactions API; GoogleADC auth uses Vertex GenerateContent)."""

from typing import ClassVar

from celeste.client import Forward
from celeste.parameters import ParameterMapper
from celeste.providers.google.auth import GoogleADC
from celeste.providers.google.interactions.config import BASE_URL
from celeste.types import TextContent

from ...client import TextClient
from .interactions import GoogleInteractionsTextClient
from .parameters import (
    GOOGLE_INTERACTIONS_PARAMETER_MAPPERS,
    GOOGLE_VERTEX_PARAMETER_MAPPERS,
)
from .vertex import GoogleVertexTextClient


class GoogleTextClient(TextClient):
    """Google text client (selects the Interactions or Vertex backend by auth)."""

    _default_base_url: ClassVar[str] = BASE_URL
    _strategy: GoogleInteractionsTextClient | GoogleVertexTextClient | None = None

    def model_post_init(self, __context: object) -> None:
        """Initialize the backend client based on auth type."""
        super().model_post_init(__context)

        StrategyClass = (
            GoogleVertexTextClient
            if isinstance(self.auth, GoogleADC)
            else GoogleInteractionsTextClient
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
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return [
            *GOOGLE_INTERACTIONS_PARAMETER_MAPPERS,
            *GOOGLE_VERTEX_PARAMETER_MAPPERS,
        ]

    _build_url = Forward()
    _init_request = Forward()
    _build_request = Forward()
    _transform_output = Forward()
    _build_metadata = Forward()
    _parse_usage = Forward()
    _parse_content = Forward()
    _parse_finish_reason = Forward()
    _parse_reasoning = Forward()
    _parse_grounding = Forward()
    _parse_tool_calls = Forward()
    _make_request = Forward()
    _make_stream_request = Forward()
    _stream_class = Forward()


__all__ = ["GoogleTextClient"]
