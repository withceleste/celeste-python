"""Ollama images client."""

import base64
from typing import Any, Unpack

from celeste.artifacts import ImageArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.ollama.generate import config
from celeste.providers.ollama.generate.client import OllamaGenerateClient
from celeste.providers.ollama.generate.streaming import (
    OllamaGenerateStream as _OllamaGenerateStream,
)

from ...client import ImagesClient
from ...io import (
    ImageChunk,
    ImageFinishReason,
    ImageInput,
    ImageOutput,
    ImageUsage,
)
from ...parameters import ImageParameters
from ...streaming import ImagesStream
from .parameters import OLLAMA_PARAMETER_MAPPERS


class OllamaImagesStream(_OllamaGenerateStream, ImagesStream):
    """Ollama NDJSON streaming for images."""

    def _parse_chunk_usage(self, event_data: dict[str, Any]) -> ImageUsage | None:
        """Parse and wrap usage from NDJSON event."""
        usage = super()._parse_chunk_usage(event_data)
        if usage:
            return ImageUsage(**usage)
        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> ImageFinishReason | None:
        """Parse and wrap finish reason from NDJSON event."""
        finish_reason = super()._parse_chunk_finish_reason(event_data)
        if finish_reason:
            return ImageFinishReason(reason=finish_reason.reason)
        return None

    def _parse_chunk(self, event_data: dict[str, Any]) -> ImageChunk | None:
        """Parse NDJSON event into ImageChunk."""
        b64_image = self._parse_chunk_content(event_data)

        if not b64_image:
            return ImageChunk(
                content=ImageArtifact(data=b""),
                metadata=self._parse_chunk_metadata(event_data),
            )

        image_bytes = base64.b64decode(b64_image)
        return ImageChunk(
            content=ImageArtifact(data=image_bytes),
            finish_reason=self._parse_chunk_finish_reason(event_data),
            usage=self._parse_chunk_usage(event_data),
            metadata=self._parse_chunk_metadata(event_data),
        )

    def _aggregate_content(self, chunks: list[ImageChunk]) -> ImageArtifact:
        """Get final image from chunks."""
        for chunk in reversed(chunks):
            if chunk.content is not None:
                return chunk.content
        msg = "No image in stream"
        raise ValueError(msg)

    def _aggregate_event_data(self, chunks: list[ImageChunk]) -> list[dict[str, Any]]:
        """Collect metadata from chunks."""
        return [chunk.metadata for chunk in chunks if chunk.metadata]


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

    def _stream_class(self) -> type[ImagesStream]:
        """Return the Stream class for Ollama images."""
        return OllamaImagesStream


__all__ = ["OllamaImagesClient", "OllamaImagesStream"]
