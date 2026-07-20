"""Google images client (Interactions API — default path)."""

from typing import Any

from celeste.artifacts import ImageArtifact
from celeste.core import UsageField
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.google.interactions import config
from celeste.providers.google.interactions.client import (
    GoogleInteractionsClient as GoogleInteractionsMixin,
)
from celeste.providers.google.utils import build_content_part
from celeste.types import ImageContent

from ...client import ImagesClient
from ...io import ImageInput
from .parameters import GOOGLE_INTERACTIONS_PARAMETER_MAPPERS


class GoogleInteractionsImagesClient(GoogleInteractionsMixin, ImagesClient):
    """Google images client (Interactions API)."""

    _edit_endpoint = config.GoogleInteractionsEndpoint.CREATE_INTERACTION

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
        return GOOGLE_INTERACTIONS_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Initialize request for Gemini image generation/edit."""
        parts: list[dict[str, Any]] = []

        # Edit uses an input image (generation omits it)
        if inputs.image is not None:
            parts.append(build_content_part(inputs.image, "image"))

        parts.append({"type": "text", "text": inputs.prompt})

        return {
            "input": [{"type": "user_input", "content": parts}],
            "response_format": {"type": "image"},
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Parse usage from response."""
        usage = super()._parse_usage(response_data)
        steps = response_data.get("steps", [])
        num_images = sum(
            1
            for step in steps
            if step.get("type") == "model_output"
            for part in step.get("content", [])
            if part.get("type") == "image"
        )
        return {**usage, UsageField.NUM_IMAGES: num_images}

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> ImageContent:
        """Parse image artifacts from the model_output step."""
        steps = super()._parse_content(response_data)
        artifacts: list[ImageArtifact] = []

        for step in steps:
            if step.get("type") != "model_output":
                continue
            for part in step.get("content", []):
                if part.get("type") != "image":
                    continue
                base64_data = part.get("data")
                if not base64_data:
                    continue
                mime_type = ImageMimeType(part.get("mime_type", "image/png"))
                artifacts.append(ImageArtifact(data=base64_data, mime_type=mime_type))

        if not artifacts:
            return ImageArtifact()
        if len(artifacts) == 1:
            return artifacts[0]
        return artifacts


__all__ = ["GoogleInteractionsImagesClient"]
