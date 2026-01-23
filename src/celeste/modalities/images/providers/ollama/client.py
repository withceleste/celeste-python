"""Ollama images client."""

import base64
from typing import Any, Unpack

from celeste.artifacts import ImageArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.ollama.generate import config
from celeste.providers.ollama.generate.client import OllamaGenerateClient

from ...client import ImagesClient
from ...io import ImageFinishReason, ImageInput, ImageOutput, ImageUsage
from ...parameters import ImageParameters
from .parameters import OLLAMA_PARAMETER_MAPPERS


class OllamaImagesClient(OllamaGenerateClient, ImagesClient):
    """Ollama images client (generate only, no edit support yet)."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return OLLAMA_PARAMETER_MAPPERS

    async def generate(
        self,
        prompt: str,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Generate images from prompt."""
        inputs = ImageInput(prompt=prompt)
        return await self._predict(
            inputs,
            endpoint=config.OllamaGenerateEndpoint.GENERATE,
            **parameters,
        )

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Build request with prompt."""
        return {"prompt": inputs.prompt}

    def _parse_usage(self, response_data: dict[str, Any]) -> ImageUsage:
        """Parse usage from response.

        Ollama image generation doesn't return usage metrics.
        """
        return ImageUsage()

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageParameters],
    ) -> ImageArtifact:
        """Parse content from response.

        Ollama returns base64-encoded image in the 'image' field.
        """
        image_b64 = super()._parse_content(response_data)
        image_bytes = base64.b64decode(image_b64)
        return ImageArtifact(data=image_bytes)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> ImageFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return ImageFinishReason(reason=finish_reason.reason)


__all__ = ["OllamaImagesClient"]
