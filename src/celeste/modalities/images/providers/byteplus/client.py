"""BytePlus images client."""

from typing import Any, Unpack

from celeste.artifacts import ImageArtifact
from celeste.exceptions import (
    ConstraintViolationError,
    StreamEventError,
    ValidationError,
)
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.byteplus.images import config
from celeste.providers.byteplus.images.client import (
    BytePlusImagesClient as BytePlusImagesMixin,
)
from celeste.providers.byteplus.images.client import (
    image_item_metadata,
)
from celeste.providers.byteplus.images.streaming import (
    BytePlusImagesStream as _BytePlusImagesStream,
)
from celeste.types import ImageContent
from celeste.utils import build_data_url, detect_mime_type

from ...client import ImagesClient
from ...io import (
    ImageChunk,
    ImageFinishReason,
    ImageInput,
    ImageUsage,
)
from ...parameters import ImageParameters
from ...streaming import ImagesStream
from .parameters import BYTEPLUS_PARAMETER_MAPPERS


def _image_mime_type(item: dict[str, Any]) -> ImageMimeType | None:
    return {
        "jpeg": ImageMimeType.JPEG,
        "png": ImageMimeType.PNG,
    }.get(str(item.get("output_format", "")).lower())


class BytePlusImagesStream(_BytePlusImagesStream, ImagesStream):
    """BytePlus streaming for images modality."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._completed_usage: ImageUsage | None = None
        self._completed_finish_reason: ImageFinishReason | None = None
        self._completed_event_data: dict[str, Any] | None = None

    def _parse_chunk(self, event_data: dict[str, Any]) -> ImageChunk | None:
        """Parse one SSE event into a typed chunk."""
        stream_error = self._parse_stream_error(event_data)
        if stream_error and (
            not self._is_error_event(event_data)
            or stream_error.get("type") == "InternalServiceError"
        ):
            return super()._parse_chunk(event_data)

        # Handle error events (partial_failed)
        if self._is_error_event(event_data):
            error = self._parse_chunk_error(event_data)
            return ImageChunk(
                content=ImageArtifact(data=b""),
                finish_reason=None,
                usage=None,
                metadata={"event_data": event_data, "error": error},
            )

        usage = self._get_chunk_usage(event_data)
        finish_reason = self._get_chunk_finish_reason(event_data)
        if finish_reason is not None:
            if usage is None or usage.num_images is None:
                raise StreamEventError(
                    "image_generation.completed is missing usage.generated_images",
                    error_type="invalid_completion",
                    event_data=event_data,
                )
            self._completed_usage = usage
            self._completed_finish_reason = finish_reason
            self._completed_event_data = event_data
            return None

        # Handle partial succeeded (image content)
        content = self._parse_chunk_content(event_data)
        if not content:
            return None

        content_type = self._parse_chunk_content_type(event_data)
        metadata = image_item_metadata(event_data)
        mime_type = _image_mime_type(event_data)
        if content_type == "url":
            artifact = ImageArtifact(
                url=content,
                mime_type=mime_type,
                metadata=metadata,
            )
        else:  # b64_json
            artifact = ImageArtifact(
                data=content,
                mime_type=mime_type,
                metadata=metadata,
            )
            if artifact.mime_type is None:
                detected = detect_mime_type(artifact.data or b"")
                if isinstance(detected, ImageMimeType):
                    artifact.mime_type = detected

        return ImageChunk(
            content=artifact,
            finish_reason=finish_reason,
            usage=None,
            metadata={"event_data": metadata},
        )

    def _aggregate_content(self, chunks: list[ImageChunk]) -> ImageContent:
        """Aggregate every successful complete image in provider index order."""
        if self._completed_event_data is None:
            raise StreamEventError(
                "BytePlus image stream ended before image_generation.completed",
                error_type="incomplete_stream",
            )
        images = [chunk.content for chunk in chunks if chunk.content.has_content]
        images.sort(
            key=lambda image: (
                image.metadata.get("image_index")
                if isinstance(image.metadata.get("image_index"), int)
                else float("inf")
            )
        )
        return images[0] if len(images) == 1 else images

    def _aggregate_usage(self, chunks: list[ImageChunk]) -> ImageUsage:
        """Override: Use usage from completed event."""
        return self._completed_usage or ImageUsage()

    def _aggregate_finish_reason(
        self, chunks: list[ImageChunk]
    ) -> ImageFinishReason | None:
        """Use the terminal completion event's finish state."""
        return self._completed_finish_reason

    def _aggregate_event_data(self, chunks: list[ImageChunk]) -> list[dict[str, Any]]:
        """Keep provider event order, including the filtered completion event."""
        events = super()._aggregate_event_data(chunks)
        if self._completed_event_data is not None:
            events.append(self._completed_event_data)
        return events


class BytePlusImagesClient(BytePlusImagesMixin, ImagesClient):
    """BytePlus image generation and editing client."""

    _generate_endpoint = config.BytePlusImagesEndpoint.CREATE_IMAGE
    _edit_endpoint = config.BytePlusImagesEndpoint.CREATE_IMAGE

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
        return BYTEPLUS_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Initialize request from BytePlus API structure."""
        request = {
            "prompt": inputs.prompt,
            "response_format": "url",
        }
        if inputs.image is not None:
            request["image"] = build_data_url(inputs.image)
        return request

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> ImageContent:
        """Parse every successful image while preserving provider order and metadata."""
        if isinstance(error := response_data.get("error"), dict):
            code = error.get("code")
            message = error.get("message", "Unknown error")
            detail = f"{code}: {message}" if code else str(message)
            raise ValidationError(f"BytePlus image generation error: {detail}")
        content = super()._parse_content(response_data)
        if not content:
            msg = "No image content found in BytePlus response"
            raise ValidationError(msg)

        images: list[ImageArtifact] = []
        for image_data in content:
            metadata = image_item_metadata(image_data)
            mime_type = _image_mime_type(image_data)
            if image_data.get("url"):
                images.append(
                    ImageArtifact(
                        url=image_data["url"],
                        mime_type=mime_type,
                        metadata=metadata,
                    )
                )
            elif image_data.get("b64_json"):
                artifact = ImageArtifact(
                    data=image_data["b64_json"],
                    mime_type=mime_type,
                    metadata=metadata,
                )
                if artifact.mime_type is None:
                    detected = detect_mime_type(artifact.data or b"")
                    if isinstance(detected, ImageMimeType):
                        artifact.mime_type = detected
                images.append(artifact)
            elif not image_data.get("error"):
                msg = "No image URL or base64 data in BytePlus response item"
                raise ValidationError(msg)

        if not images and not all(image.get("error") for image in content):
            msg = "No successful images found in BytePlus response"
            raise ValidationError(msg)
        return images[0] if len(images) == 1 else images

    def _build_request(
        self,
        inputs: ImageInput,
        extra_body: dict[str, Any] | None = None,
        streaming: bool = False,
        **parameters: Unpack[ImageParameters],
    ) -> dict[str, Any]:
        """Build a request while preserving BytePlus size-field exclusivity."""
        if (
            parameters.get("aspect_ratio") is not None
            and parameters.get("quality") is not None
        ):
            msg = (
                "Cannot use both 'aspect_ratio' and 'quality' parameters. "
                "BytePlus's 'size' field supports two methods that cannot be combined:\n"
                "  • quality: Resolution class (for example, '1K' or '2K')\n"
                "  • aspect_ratio: Exact dimensions (for example, '2048x2048')\n"
                "Use one or the other, not both."
            )
            raise ConstraintViolationError(msg)

        return super()._build_request(
            inputs,
            extra_body=extra_body,
            streaming=streaming,
            **parameters,
        )

    def _stream_class(self) -> type[ImagesStream]:
        """Return the Stream class for this provider."""
        return BytePlusImagesStream


__all__ = ["BytePlusImagesClient", "BytePlusImagesStream"]
