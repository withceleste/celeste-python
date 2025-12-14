"""Parameters for image generation."""

from enum import StrEnum

from celeste.parameters import Parameters


class ImageGenerationParameter(StrEnum):
    """Unified parameter names for image generation capability."""

    ASPECT_RATIO = "aspect_ratio"
    GUIDANCE = "guidance"
    OUTPUT_FORMAT = "output_format"
    PARTIAL_IMAGES = "partial_images"
    PROMPT_UPSAMPLING = "prompt_upsampling"
    QUALITY = "quality"
    SAFETY_TOLERANCE = "safety_tolerance"
    SEED = "seed"
    STEPS = "steps"
    WATERMARK = "watermark"


class ImageGenerationParameters(Parameters):
    """Parameters for image generation."""

    aspect_ratio: str | None
    guidance: float | None
    output_format: str | None
    partial_images: int | None
    prompt_upsampling: bool | None
    quality: str | None
    safety_tolerance: int | None
    seed: int | None
    steps: int | None
    watermark: bool | None
