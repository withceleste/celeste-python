"""Google videos client (Veo by model family; Omni models use Interactions)."""

from typing import Any, Unpack

from celeste.artifacts import VideoArtifact
from celeste.parameters import ParameterMapper
from celeste.types import VideoContent

from ...client import VideosClient
from ...io import VideoFinishReason, VideoInput
from ...parameters import VideoParameters
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

        if strategy._generate_endpoint is not None:
            object.__setattr__(self, "_generate_endpoint", strategy._generate_endpoint)
        if strategy._edit_endpoint is not None:
            object.__setattr__(self, "_edit_endpoint", strategy._edit_endpoint)

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[VideoContent]]:
        return [
            *GOOGLE_VEO_PARAMETER_MAPPERS,
            *GOOGLE_INTERACTIONS_PARAMETER_MAPPERS,
        ]

    def _init_request(self, inputs: VideoInput) -> dict[str, Any]:
        return self._strategy._init_request(inputs)  # type: ignore[union-attr]

    def _build_request(
        self,
        inputs: VideoInput,
        **parameters: Unpack[VideoParameters],
    ) -> dict[str, Any]:
        return self._strategy._build_request(inputs, **parameters)  # type: ignore[union-attr]

    def _transform_output(
        self, content: VideoContent, **parameters: Unpack[VideoParameters]
    ) -> VideoContent:
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
    ) -> VideoContent:
        return self._strategy._parse_content(response_data)  # type: ignore[union-attr]

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> VideoFinishReason:
        return self._strategy._parse_finish_reason(response_data)  # type: ignore[union-attr]

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[VideoParameters],
    ) -> dict[str, Any]:
        return await self._strategy._make_request(  # type: ignore[union-attr]
            request_body,
            endpoint=endpoint,
            extra_headers=extra_headers,
            **parameters,
        )

    async def download_content(self, artifact: VideoArtifact) -> VideoArtifact:
        return await self._strategy.download_content(artifact)  # type: ignore[union-attr]


__all__ = ["GoogleVideosClient"]
