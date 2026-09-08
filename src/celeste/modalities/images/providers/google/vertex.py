"""Google images client (Vertex / GenerateContent, GoogleADC auth only)."""

from typing import Any

from celeste.artifacts import ImageArtifact
from celeste.core import UsageField
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.google.generate_content import config
from celeste.providers.google.generate_content.client import (
    GoogleGenerateContentClient as GoogleGenerateContentMixin,
)
from celeste.providers.google.utils import build_media_part
from celeste.types import ImageContent

from ...client import ImagesClient
from ...io import ImageFinishReason, ImageInput
from .parameters import GOOGLE_VERTEX_PARAMETER_MAPPERS


class GoogleVertexImagesClient(GoogleGenerateContentMixin, ImagesClient):
    """Google images client (Vertex / GenerateContent)."""

    _edit_endpoint = config.GoogleGenerateContentEndpoint.GENERATE_CONTENT

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
        return GOOGLE_VERTEX_PARAMETER_MAPPERS

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Retain ordered text and candidate safety/grounding without image payloads."""
        metadata = super()._build_metadata(response_data)
        candidates = response_data.get("candidates", [])
        metadata["text_blocks"] = [
            {**part, "candidate_index": i, "part_index": j}
            for i, candidate in enumerate(candidates)
            for j, part in enumerate(candidate.get("content", {}).get("parts", []))
            if not part.get("thought") and "text" in part
        ]
        if "candidates" in response_data:
            metadata["raw_response"]["candidates"] = [
                {k: v for k, v in candidate.items() if k != "content"}
                for candidate in candidates
            ]
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
            if not part.get("thought")
            and (
                part.get("inlineData", {}).get("data")
                or part.get("fileData", {}).get("fileUri")
            )
        )
        return {**usage, UsageField.NUM_IMAGES: num_images}

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> ImageContent:
        """Parse image artifacts from Gemini candidates."""
        if not response_data.get("candidates") and response_data.get(
            "promptFeedback", {}
        ).get("blockReason"):
            return ImageArtifact()
        candidates = super()._parse_content(response_data)
        artifacts: list[ImageArtifact] = []

        for i, candidate in enumerate(candidates):
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            for j, part in enumerate(parts):
                if part.get("thought"):
                    continue
                inline_data = part.get("inlineData", {})
                base64_data = inline_data.get("data")
                file_data = part.get("fileData", {})
                uri = file_data.get("fileUri")
                if not base64_data and not uri:
                    continue
                mime_value = inline_data.get("mimeType") or file_data.get("mimeType")
                artifacts.append(
                    ImageArtifact(
                        data=base64_data,
                        url=uri,
                        mime_type=ImageMimeType(mime_value) if mime_value else None,
                        metadata={
                            **{
                                k: v
                                for k, v in part.items()
                                if k not in {"inlineData", "fileData"}
                            },
                            "candidate_index": i,
                            "part_index": j,
                        },
                    )
                )

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
            return ImageFinishReason(
                reason=finish_reason.reason, message=candidates[0].get("finishMessage")
            )
        prompt_feedback = response_data.get("promptFeedback", {})
        return ImageFinishReason(
            reason=prompt_feedback.get("blockReason"),
            message=prompt_feedback.get("blockReasonMessage"),
        )


__all__ = ["GoogleVertexImagesClient"]
