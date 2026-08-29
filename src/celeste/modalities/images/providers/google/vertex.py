"""Google images client (Vertex / GenerateContent, GoogleADC auth only)."""

from typing import Any

from celeste.artifacts import ImageArtifact
from celeste.core import UsageField
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.google.auth import GoogleADC
from celeste.providers.google.generate_content import config
from celeste.providers.google.generate_content.client import (
    GoogleGenerateContentClient as GoogleGenerateContentMixin,
)
from celeste.providers.google.utils import build_media_part
from celeste.types import ImageContent

from ...client import ImagesClient
from ...io import ImageFinishReason, ImageInput
from .parameters import GOOGLE_VERTEX_PARAMETER_MAPPERS

_GLOBAL_ONLY_MODEL_IDS = frozenset(
    {
        "gemini-3-pro-image",
        "gemini-3.1-flash-image",
        "gemini-3.1-flash-lite-image",
    }
)


class GoogleVertexImagesClient(GoogleGenerateContentMixin, ImagesClient):
    """Google images client (Vertex / GenerateContent)."""

    _edit_endpoint = config.GoogleGenerateContentEndpoint.GENERATE_CONTENT

    def model_post_init(self, __context: object) -> None:
        """Enforce model-specific Vertex AI location availability."""
        super().model_post_init(__context)
        if (
            self.model.id in _GLOBAL_ONLY_MODEL_IDS
            and isinstance(self.auth, GoogleADC)
            and self.auth.location != "global"
        ):
            raise ValueError(
                f"{self.model.id} is only available in the global Vertex AI location"
            )

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
        return GOOGLE_VERTEX_PARAMETER_MAPPERS

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Preserve billing metadata without retaining generated image content."""
        metadata = super()._build_metadata(response_data)
        web_query_count = 0
        image_query_count = 0
        for candidate in response_data.get("candidates", []):
            grounding_metadata = candidate.get("groundingMetadata", {})
            web_query_count += len(grounding_metadata.get("webSearchQueries") or [])
            image_query_count += len(grounding_metadata.get("imageSearchQueries") or [])
        if web_query_count or image_query_count:
            metadata["raw_response"]["grounding_web_query_count"] = web_query_count
            metadata["raw_response"]["grounding_image_query_count"] = image_query_count
        return metadata

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Initialize request for Gemini image generation/edit."""
        parts: list[dict[str, Any]] = []

        # Edit uses an input image (generation omits it)
        if inputs.image is not None:
            parts.append(build_media_part(inputs.image))

        parts.append({"text": inputs.prompt})

        return {
            "contents": [{"role": "user", "parts": parts}],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
                "imageConfig": {},
            },
        }

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        """Parse usage from response."""
        usage = super()._parse_usage(response_data)
        candidates = response_data.get("candidates", [])
        num_images = sum(
            1
            for candidate in candidates
            for part in candidate.get("content", {}).get("parts", [])
            if not part.get("thought") and part.get("inlineData", {}).get("data")
        )
        return {**usage, UsageField.NUM_IMAGES: num_images}

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> ImageContent:
        """Parse image artifacts from Gemini candidates."""
        if not response_data.get("candidates") and "promptFeedback" in response_data:
            return ImageArtifact()
        candidates = super()._parse_content(response_data)
        artifacts: list[ImageArtifact] = []

        for candidate in candidates:
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            for part in parts:
                if part.get("thought"):
                    continue
                inline_data = part.get("inlineData", {})
                base64_data = inline_data.get("data")
                if not base64_data:
                    continue
                mime_type = ImageMimeType(inline_data.get("mimeType", "image/png"))
                artifacts.append(ImageArtifact(data=base64_data, mime_type=mime_type))

        if not artifacts:
            return ImageArtifact()
        if len(artifacts) == 1:
            return artifacts[0]
        return artifacts

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> ImageFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        candidates = response_data.get("candidates", [])
        if candidates:
            finish_message = candidates[0].get("finishMessage")
            return ImageFinishReason(
                reason=finish_reason.reason, message=finish_message
            )

        prompt_feedback = response_data.get("promptFeedback", {})
        return ImageFinishReason(
            reason=prompt_feedback.get("blockReason"),
            message=prompt_feedback.get("blockReasonMessage"),
        )


__all__ = ["GoogleVertexImagesClient"]
