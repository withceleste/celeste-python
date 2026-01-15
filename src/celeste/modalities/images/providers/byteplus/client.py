"""BytePlus images client."""

import base64
from typing import Any, Unpack

from celeste.artifacts import ImageArtifact
from celeste.exceptions import ConstraintViolationError, ValidationError
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.byteplus.images import config
from celeste.providers.byteplus.images.client import (
    BytePlusImagesClient as BytePlusImagesMixin,
)
from celeste.providers.byteplus.images.streaming import (
    BytePlusImagesStream as _BytePlusImagesStream,
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
from .parameters import BYTEPLUS_PARAMETER_MAPPERS


class BytePlusImagesStream(_BytePlusImagesStream, ImagesStream):
    """BytePlus streaming for images modality."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._completed_usage: ImageUsage | None = None
        self._completed_event_data: dict[str, Any] | None = None

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
        # Handle error events (partial_failed)
        if self._is_error_event(event_data):
            error = self._parse_chunk_error(event_data)
            return ImageChunk(
                content=ImageArtifact(data=b""),
                finish_reason=None,
                usage=None,
                metadata={"event_data": event_data, "error": error},
            )

        # Handle completed event (usage only)
        usage = self._parse_chunk_usage(event_data)
        if usage is not None:
            self._completed_usage = usage
            self._completed_event_data = event_data
            return None

        # Handle partial succeeded (image content)
        content = self._parse_chunk_content(event_data)
        if not content:
            return None

        content_type = self._parse_chunk_content_type(event_data)
        if content_type == "url":
            artifact = ImageArtifact(url=content, mime_type=ImageMimeType.PNG)
        else:  # b64_json
            image_data = base64.b64decode(content)
            artifact = ImageArtifact(data=image_data)

        return ImageChunk(
            content=artifact,
            finish_reason=self._parse_chunk_finish_reason(event_data),
            usage=None,
            metadata={"event_data": event_data},
        )

    def _aggregate_content(self, chunks: list[ImageChunk]) -> ImageArtifact:
        """Aggregate image content from chunks."""
        return chunks[-1].content

    def _aggregate_usage(self, chunks: list[ImageChunk]) -> ImageUsage:
        """Override: Use usage from completed event."""
        if self._completed_usage is not None:
            return self._completed_usage
        return super()._aggregate_usage(chunks)

    def _aggregate_event_data(self, chunks: list[ImageChunk]) -> list[dict[str, Any]]:
        """Collect metadata events (skip content-only events)."""
        events: list[dict[str, Any]] = []
        if self._completed_event_data is not None:
            events.append(self._completed_event_data)
        for chunk in chunks:
            event_data = chunk.metadata.get("event_data")
            if isinstance(event_data, dict):
                events.append(event_data)
        return events


class BytePlusImagesClient(BytePlusImagesMixin, ImagesClient):
    """BytePlus images client (generate + streaming)."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return BYTEPLUS_PARAMETER_MAPPERS

    async def generate(
        self,
        prompt: str,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Generate images from prompt."""
        inputs = ImageInput(prompt=prompt)
        return await self._predict(
            inputs,
            endpoint=config.BytePlusImagesEndpoint.CREATE_IMAGE,
            **parameters,
        )

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Initialize request from BytePlus API structure."""
        return {
            "prompt": inputs.prompt,
            "response_format": "url",
        }

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
        content = super()._parse_content(response_data)
        if not content:
            msg = "No image content found in BytePlus response"
            raise ValidationError(msg)

        image_data = content[0]
        if image_data.get("url"):
            return ImageArtifact(
                url=image_data["url"],
                mime_type=ImageMimeType.PNG,
            )
        if image_data.get("b64_json"):
            image_bytes = base64.b64decode(image_data["b64_json"])
            return ImageArtifact(
                data=image_bytes,
                mime_type=ImageMimeType.PNG,
            )

        msg = "No image URL or base64 data in BytePlus response"
        raise ValidationError(msg)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> ImageFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return ImageFinishReason(reason=finish_reason.reason)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Unpack[ImageParameters],
    ) -> dict[str, Any]:
        """Make HTTP request with parameter validation."""
        # Validate mutually exclusive parameters
        if parameters.get("aspect_ratio") and parameters.get("quality"):
            msg = (
                "Cannot use both 'aspect_ratio' and 'quality' parameters. "
                "BytePlus's 'size' field supports two methods that cannot be combined:\n"
                "  • quality: Resolution class ('1K', '2K', '4K')\n"
                "  • aspect_ratio: Exact dimensions (e.g., '2048x2048', '3840x2160')\n"
                "Use one or the other, not both."
            )
            raise ConstraintViolationError(msg)

        return await super()._make_request(
            request_body, endpoint=endpoint, **parameters
        )

    def _stream_class(self) -> type[ImagesStream]:
        """Return the Stream class for this provider."""
        return BytePlusImagesStream


__all__ = ["BytePlusImagesClient", "BytePlusImagesStream"]
