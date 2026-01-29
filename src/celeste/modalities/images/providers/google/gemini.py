"""Gemini client for Google images modality."""

import base64
from typing import Any, Unpack

from celeste.artifacts import ImageArtifact
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.google.generate_content import config as google_config
from celeste.providers.google.generate_content.client import GoogleGenerateContentClient
from celeste.types import ImageContent

from ...client import ImagesClient
from ...io import ImageFinishReason, ImageInput, ImageOutput, ImageUsage
from ...parameters import ImageParameters
from .parameters import GEMINI_PARAMETER_MAPPERS


def _build_image_part(image: ImageArtifact) -> dict[str, Any]:
    """Build a Gemini image part from an ImageArtifact (snake_case, provider-style)."""
    if image.url:
        return {"file_data": {"file_uri": image.url}}

    if image.data is not None:
        image_bytes = image.data
    elif image.path:
        with open(image.path, "rb") as f:
            image_bytes = f.read()
    else:
        msg = "ImageArtifact must have url, data, or path"
        raise ValueError(msg)

    base64_data = base64.b64encode(image_bytes).decode("utf-8")
    return {
        "inline_data": {
            "mime_type": image.mime_type,
            "data": base64_data,
        }
    }


class GeminiImagesClient(GoogleGenerateContentClient, ImagesClient):
    """Google Gemini client for images modality (generate + edit)."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return GEMINI_PARAMETER_MAPPERS

    async def generate(
        self,
        prompt: str,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        inputs = ImageInput(prompt=prompt)
        return await self._predict(
            inputs,
            endpoint=google_config.GoogleGenerateContentEndpoint.GENERATE_CONTENT,
            **parameters,
        )

    async def edit(
        self,
        image: ImageArtifact,
        prompt: str,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        inputs = ImageInput(prompt=prompt, image=image)
        return await self._predict(
            inputs,
            endpoint=google_config.GoogleGenerateContentEndpoint.GENERATE_CONTENT,
            **parameters,
        )

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Initialize request for Gemini image generation/edit."""
        parts: list[dict[str, Any]] = []

        # Edit uses an input image (generation omits it)
        if inputs.image is not None:
            parts.append(_build_image_part(inputs.image))

        parts.append({"text": inputs.prompt})

        return {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
                "imageConfig": {},
            },
        }

    def _parse_usage(self, response_data: dict[str, Any]) -> ImageUsage:
        """Parse usage from response."""
        usage = super()._parse_usage(response_data)
        candidates = response_data.get("candidates", [])
        return ImageUsage(**usage, num_images=len(candidates))

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageParameters],
    ) -> ImageContent:
        """Parse image artifacts from Gemini candidates."""
        candidates = super()._parse_content(response_data)
        artifacts: list[ImageArtifact] = []

        for candidate in candidates:
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            for part in parts:
                inline_data = part.get("inlineData", {})
                base64_data = inline_data.get("data")
                if not base64_data:
                    continue
                mime_type = ImageMimeType(inline_data.get("mimeType", "image/png"))
                image_bytes = base64.b64decode(base64_data)
                artifacts.append(ImageArtifact(data=image_bytes, mime_type=mime_type))

        if not artifacts:
            return ImageArtifact()
        if len(artifacts) == 1:
            return artifacts[0]
        return artifacts

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> ImageFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        candidates = response_data.get("candidates", [])
        finish_message = candidates[0].get("finishMessage") if candidates else None
        return ImageFinishReason(reason=finish_reason.reason, message=finish_message)


__all__ = ["GeminiImagesClient"]
