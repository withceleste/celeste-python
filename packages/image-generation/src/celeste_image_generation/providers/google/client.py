"""Google client implementation."""

import base64
from typing import Any, Unpack

import httpx
from pydantic import ConfigDict

from celeste.artifacts import ImageArtifact
from celeste.core import Provider
from celeste.exceptions import ModelNotFoundError
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste_image_generation.client import ImageGenerationClient
from celeste_image_generation.io import (
    ImageGenerationFinishReason,
    ImageGenerationInput,
    ImageGenerationUsage,
)
from celeste_image_generation.parameters import ImageGenerationParameters

from . import config
from .parameters import GOOGLE_PARAMETER_MAPPERS


class GoogleImageGenerationClient(ImageGenerationClient):
    """Google client for image generation.

    Supports both Imagen API and Gemini multimodal API via adapter pattern.
    Adapter selection happens automatically based on model type.
    """

    model_config = ConfigDict(extra="allow")

    def model_post_init(self, __context: Any) -> None:  # noqa: ANN401
        """Initialize API adapter based on model type."""
        super().model_post_init(__context)

        adapter_class, _ = _get_adapter_for_model(self.model.id)
        self.api = adapter_class()
        self.endpoint = self.api.endpoint(self.model.id)

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        """Return parameter mappers for Google provider."""
        return GOOGLE_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageGenerationInput) -> dict[str, Any]:
        """Initialize request using API adapter."""
        return self.api.build_request(inputs.prompt, {})

    def _parse_usage(self, response_data: dict[str, Any]) -> ImageGenerationUsage:
        """Parse usage from response using API adapter."""
        return self.api.parse_usage(response_data)

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> ImageArtifact:
        """Parse content from response using API adapter."""
        prediction = self.api.parse_response(response_data)

        if prediction is None:
            return ImageArtifact()

        base64_data = prediction.get("bytesBase64Encoded") or prediction["data"]
        mime_type = ImageMimeType(prediction.get("mimeType", "image/png"))
        image_bytes = base64.b64decode(base64_data)

        return ImageArtifact(data=image_bytes, mime_type=mime_type)

    def _parse_finish_reason(
        self, response_data: dict[str, Any]
    ) -> ImageGenerationFinishReason | None:
        """Parse finish reason from provider response.

        For Gemini models, extracts finishReason from candidates[0].
        For Imagen models, returns None (not provided).
        """
        # Check if this is a Gemini response (has "candidates")
        candidates = response_data.get("candidates")
        if candidates:
            candidate = candidates[0]
            finish_reason_str = candidate.get("finishReason")
            if finish_reason_str:
                finish_message = candidate.get("finishMessage")
                return ImageGenerationFinishReason(
                    reason=finish_reason_str,
                    message=finish_message,
                )
        # Imagen models don't provide finish reasons
        return None

    def _build_metadata(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Build metadata dictionary from response data."""
        # Parse finish_reason from full response_data before calling super (needs "candidates")
        finish_reason = self._parse_finish_reason(response_data)

        metadata = super()._build_metadata(response_data)
        # Override with pre-parsed finish_reason
        if finish_reason is not None:
            metadata["finish_reason"] = finish_reason
        return metadata

    async def _make_request(
        self,
        request_body: dict[str, Any],
        **parameters: Unpack[ImageGenerationParameters],
    ) -> httpx.Response:
        """Make HTTP request(s) and return response object."""
        headers = {
            config.AUTH_HEADER_NAME: self.api_key.get_secret_value(),
            "Content-Type": "application/json",
        }

        return await self.http_client.post(
            f"{config.BASE_URL}{self.endpoint}",
            headers=headers,
            json_body=request_body,
        )


def _get_adapter_for_model(model_id: str) -> tuple[type, str]:
    """Get adapter class and endpoint for model ID.

    Returns:
        Tuple of (adapter_class, endpoint_template).
    """
    from .models import GEMINI_MODELS, IMAGEN_MODELS

    # Create sets for O(1) lookup (computed once per import)
    imagen_model_ids = {model.id for model in IMAGEN_MODELS}
    gemini_model_ids = {model.id for model in GEMINI_MODELS}

    if model_id in imagen_model_ids:
        from .imagen_api import ImagenAPIAdapter

        return ImagenAPIAdapter, config.IMAGEN_ENDPOINT
    if model_id in gemini_model_ids:
        from .gemini_api import GeminiImageAPIAdapter

        return GeminiImageAPIAdapter, config.GEMINI_ENDPOINT

    raise ModelNotFoundError(model_id=model_id, provider=Provider.GOOGLE)


__all__ = ["GoogleImageGenerationClient"]
