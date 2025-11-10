"""Parameters for image generation."""

from enum import StrEnum

from celeste.parameters import Parameters


class ImageGenerationParameter(StrEnum):
    """Unified parameter names for image generation capability."""

    ASPECT_RATIO = "aspect_ratio"
    PARTIAL_IMAGES = "partial_images"
    QUALITY = "quality"
    WATERMARK = "watermark"


class ImageGenerationParameters(Parameters):
    """Parameters for image generation."""

    aspect_ratio: str | None
    partial_images: int | None
    quality: str | None
    watermark: bool | None
