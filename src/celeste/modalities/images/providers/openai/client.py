"""OpenAI images client."""

import base64
from typing import Any, Unpack

from celeste.artifacts import ImageArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.openai.images import config
from celeste.providers.openai.images.client import (
    OpenAIImagesClient as OpenAIImagesMixin,
)
from celeste.providers.openai.images.streaming import (
    OpenAIImagesStream as _OpenAIImagesStream,
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
from .parameters import OPENAI_PARAMETER_MAPPERS


class OpenAIImagesStream(_OpenAIImagesStream, ImagesStream):
    """OpenAI streaming for images modality."""

    def _parse_chunk_usage(self, event_data: dict[str, Any]) -> ImageUsage | None:
        """Parse and wrap usage from SSE event."""
        usage = super()._parse_chunk_usage(event_data)
        if usage:
            return ImageUsage(**usage)
        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> ImageFinishReason | None:
        """Parse and wrap finish reason from SSE event."""
        finish_reason = super()._parse_chunk_finish_reason(event_data)
        if finish_reason:
            return ImageFinishReason(reason=finish_reason.reason)
        return None

    def _parse_chunk(self, event_data: dict[str, Any]) -> ImageChunk | None:
        """Parse one SSE event into a typed chunk."""
        b64_json = self._parse_chunk_content(event_data)
        if not b64_json:
            usage = self._parse_chunk_usage(event_data)
            finish_reason = self._parse_chunk_finish_reason(event_data)
            if usage is None and finish_reason is None:
                return None
            # Chunk with usage/finish_reason only (no image)
            return ImageChunk(
                content=ImageArtifact(data=b""),
                finish_reason=finish_reason,
                usage=usage,
                metadata={"event_data": event_data},
            )

        image_data = base64.b64decode(b64_json)
        artifact = ImageArtifact(data=image_data)

        return ImageChunk(
            content=artifact,
            finish_reason=self._parse_chunk_finish_reason(event_data),
            usage=self._parse_chunk_usage(event_data),
            metadata={"event_data": event_data},
        )

    def _aggregate_content(self, chunks: list[ImageChunk]) -> ImageArtifact:
        """Aggregate image content from chunks."""
        return chunks[-1].content

    def _aggregate_event_data(self, chunks: list[ImageChunk]) -> list[dict[str, Any]]:
        """Collect metadata events (skip content-only events)."""
        events: list[dict[str, Any]] = []
        for chunk in chunks:
            event_data = chunk.metadata.get("event_data")
            if isinstance(event_data, dict):
                events.append(event_data)
        return events


class OpenAIImagesClient(OpenAIImagesMixin, ImagesClient):
    """OpenAI images client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return OPENAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Initialize request, keeping ImageArtifact for multipart handling."""
        request: dict[str, Any] = {"prompt": inputs.prompt}
        if inputs.image is not None:
            # Keep as ImageArtifact - _make_multipart_request handles encoding
            request["image"] = inputs.image
        return request

    async def generate(
        self,
        prompt: str,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Generate images from prompt."""
        inputs = ImageInput(prompt=prompt)
        return await self._predict(
            inputs,
            endpoint=config.OpenAIImagesEndpoint.CREATE_IMAGE,
            **parameters,
        )

    async def edit(
        self,
        image: ImageArtifact,
        prompt: str,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Edit an image with text instructions."""
        inputs = ImageInput(image=image, prompt=prompt)
        return await self._predict(
            inputs,
            endpoint=config.OpenAIImagesEndpoint.CREATE_EDIT,
            **parameters,
        )

    def _parse_usage(self, response_data: dict[str, Any]) -> ImageUsage:
        """Parse usage from response."""
        usage = super()._parse_usage(response_data)
        return ImageUsage(**usage)

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageParameters],
    ) -> ImageArtifact:
        """Parse content from response."""
        data = super()._parse_content(response_data)
        image_data = data[0]

        b64_json = image_data.get("b64_json")
        if b64_json:
            image_bytes = base64.b64decode(b64_json)
            return ImageArtifact(data=image_bytes)

        url = image_data.get("url")
        if url:
            return ImageArtifact(url=url)

        msg = "No image URL or base64 data in response"
        raise ValueError(msg)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> ImageFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return ImageFinishReason(reason=finish_reason.reason)

    def _stream_class(self) -> type[ImagesStream]:
        """Return the Stream class for this provider."""
        return OpenAIImagesStream


__all__ = ["OpenAIImagesClient", "OpenAIImagesStream"]
