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
from celeste.types import ImageContent
from celeste.utils import build_data_url, detect_mime_type

from ...client import ImagesClient
from ...io import (
    ImageChunk,
    ImageInput,
    ImageUsage,
)
from ...parameters import ImageParameters
from ...streaming import ImagesStream
from .parameters import BYTEPLUS_PARAMETER_MAPPERS

_OUTPUT_FORMAT_MIME_TYPES = {"png": ImageMimeType.PNG, "jpeg": ImageMimeType.JPEG}


def _image_mime_type(
    image_data: dict[str, Any], data: bytes | None = None
) -> ImageMimeType | None:
    """Return the MIME type of the declared output_format, else detect it from data."""
    declared = _OUTPUT_FORMAT_MIME_TYPES.get(image_data.get("output_format", ""))
    if declared is not None or data is None:
        return declared
    detected = detect_mime_type(data)
    return detected if isinstance(detected, ImageMimeType) else None


class BytePlusImagesStream(_BytePlusImagesStream, ImagesStream):
    """BytePlus streaming for images modality."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._completed_usage: ImageUsage | None = None
        self._completed_event_data: dict[str, Any] | None = None

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
        usage = self._get_chunk_usage(event_data)
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
            artifact = ImageArtifact(
                url=content, mime_type=_image_mime_type(event_data)
            )
        else:  # b64_json
            data = base64.b64decode(content)
            artifact = ImageArtifact(
                data=data, mime_type=_image_mime_type(event_data, data)
            )

        return ImageChunk(
            content=artifact,
            finish_reason=self._get_chunk_finish_reason(event_data),
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
        """Prepend completed_event_data, then delegate to base."""
        events: list[dict[str, Any]] = []
        if self._completed_event_data is not None:
            events.append(self._completed_event_data)
        events.extend(super()._aggregate_event_data(chunks))
        return events


class BytePlusImagesClient(BytePlusImagesMixin, ImagesClient):
    """BytePlus images client (generate + edit + streaming)."""

    _generate_endpoint = config.BytePlusImagesEndpoint.CREATE_IMAGE
    _edit_endpoint = config.BytePlusImagesEndpoint.CREATE_IMAGE

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
        return BYTEPLUS_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Initialize request from BytePlus API structure."""
        request: dict[str, Any] = {
            "prompt": inputs.prompt,
            "response_format": "url",
        }
        if inputs.image is not None:
            request["image"] = build_data_url(inputs.image)
        return request

    def _parse_content(
        self,
        response_data: dict[str, Any],
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
                mime_type=_image_mime_type(image_data),
            )
        if image_data.get("b64_json"):
            data = base64.b64decode(image_data["b64_json"])
            return ImageArtifact(
                data=data,
                mime_type=_image_mime_type(image_data, data),
            )

        msg = "No image URL or base64 data in BytePlus response"
        raise ValidationError(msg)

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
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
            request_body, endpoint=endpoint, extra_headers=extra_headers, **parameters
        )

    def _stream_class(self) -> type[ImagesStream]:
        """Return the Stream class for this provider."""
        return BytePlusImagesStream


__all__ = ["BytePlusImagesClient", "BytePlusImagesStream"]
