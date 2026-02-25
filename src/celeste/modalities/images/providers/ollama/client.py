"""Ollama images client."""

from typing import Any, Unpack

from celeste.artifacts import ImageArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.ollama.generate import config
from celeste.providers.ollama.generate.client import OllamaGenerateClient
from celeste.providers.ollama.generate.streaming import (
    OllamaGenerateStream as _OllamaGenerateStream,
)
from celeste.types import ImageContent

from ...client import ImagesClient
from ...io import (
    ImageChunk,
    ImageInput,
    ImageOutput,
)
from ...parameters import ImageParameters
from ...streaming import ImagesStream
from .parameters import OLLAMA_PARAMETER_MAPPERS


class OllamaImagesStream(_OllamaGenerateStream, ImagesStream):
    """Ollama NDJSON streaming for images."""

    def _parse_chunk(self, event_data: dict[str, Any]) -> ImageChunk | None:
        """Parse NDJSON event into ImageChunk."""
        b64_image = self._parse_chunk_content(event_data)

        if not b64_image:
            return ImageChunk(
                content=ImageArtifact(data=b""),
                metadata={"event_data": event_data},
            )

        return ImageChunk(
            content=ImageArtifact(data=b64_image),
            finish_reason=self._get_chunk_finish_reason(event_data),
            usage=self._get_chunk_usage(event_data),
            metadata={"event_data": event_data},
        )

    def _aggregate_content(self, chunks: list[ImageChunk]) -> ImageArtifact:
        """Get final image from chunks."""
        for chunk in reversed(chunks):
            if chunk.content is not None:
                return chunk.content
        msg = "No image in stream"
        raise ValueError(msg)


class OllamaImagesClient(OllamaGenerateClient, ImagesClient):
    """Ollama images client (generate only, no edit support yet)."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
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

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Parse usage from response.

        Ollama image generation doesn't return usage metrics.
        """
        return {}

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageParameters],
    ) -> ImageArtifact:
        """Parse content from response.

        Ollama returns base64-encoded image in the 'image' field.
        """
        image_b64 = super()._parse_content(response_data)
        return ImageArtifact(data=image_b64)

    def _stream_class(self) -> type[ImagesStream]:
        """Return the Stream class for Ollama images."""
        return OllamaImagesStream


__all__ = ["OllamaImagesClient", "OllamaImagesStream"]
