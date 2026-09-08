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

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Retain text positions and executed search counts without image payloads."""
        metadata = super()._build_metadata(response_data)
        steps = response_data.get("steps", [])
        metadata["text_blocks"] = [
            {**part, "step_index": i, "part_index": j}
            for i, step in enumerate(steps)
            if step.get("type") == "model_output"
            for j, part in enumerate(step.get("content", []))
            if part.get("type") == "text"
        ]
        if "steps" in response_data:
            metadata["raw_response"]["grounding_query_count"] = sum(
                len(step.get("arguments", {}).get("queries") or [])
                for step in steps
                if step.get("type") == "google_search_call"
            )
        return metadata

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
            if part.get("type") == "image" and (part.get("data") or part.get("uri"))
        )
        return {**usage, UsageField.NUM_IMAGES: num_images}

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> ImageContent:
        """Parse image artifacts from the model_output step."""
        steps = super()._parse_content(response_data)
        artifacts: list[ImageArtifact] = []

        for i, step in enumerate(steps):
            if step.get("type") != "model_output":
                continue
            for j, part in enumerate(step.get("content", [])):
                if part.get("type") != "image":
                    continue
                base64_data = part.get("data")
                uri = part.get("uri")
                if not base64_data and not uri:
                    continue
                mime_value = part.get("mime_type")
                artifacts.append(
                    ImageArtifact(
                        data=base64_data,
                        url=uri,
                        mime_type=ImageMimeType(mime_value) if mime_value else None,
                        metadata={
                            **{
                                k: v
                                for k, v in part.items()
                                if k not in {"data", "uri", "mime_type", "type"}
                            },
                            "step_index": i,
                            "part_index": j,
                        },
                    )
                )

        if not artifacts:
            return ImageArtifact()
        if len(artifacts) == 1:
            return artifacts[0]
        return artifacts


__all__ = ["GoogleInteractionsImagesClient"]
