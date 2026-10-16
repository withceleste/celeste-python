"""BFL images client (FLUX.1 models)."""

from typing import Any

from celeste.artifacts import ImageArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.bfl.flux import config
from celeste.providers.bfl.flux.client import BFLFluxClient as BFLFluxMixin
from celeste.types import ImageContent

from ...client import ImagesClient
from ...io import ImageInput
from .parameters import BFL_FLUX1_PARAMETER_MAPPERS


class BFLFlux1ImagesClient(BFLFluxMixin, ImagesClient):
    """BFL images client for FLUX.1 (generate)."""

    _generate_endpoint = config.BFLFluxEndpoint.CREATE_TASK

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
        return BFL_FLUX1_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Build request with prompt."""
        return {"prompt": inputs.prompt}

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> ImageArtifact:
        """Parse content from response."""
        result = super()._parse_content(response_data)
        sample_url = result.get("sample")

        if not sample_url:
            msg = f"No image URL in {self.provider} response"
            raise ValueError(msg)

        return ImageArtifact(url=sample_url)


__all__ = ["BFLFlux1ImagesClient"]
