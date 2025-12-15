"""Parameters for image generation."""

from enum import StrEnum

from celeste.artifacts import ImageArtifact
from celeste.parameters import Parameters


class ImageGenerationParameter(StrEnum):
    """Unified parameter names for image generation capability."""

    ASPECT_RATIO = "aspect_ratio"
    NUM_IMAGES = "num_images"
    PARTIAL_IMAGES = "partial_images"
    QUALITY = "quality"
    WATERMARK = "watermark"
    REFERENCE_IMAGES = "reference_images"
    PROMPT_UPSAMPLING = "prompt_upsampling"
    SEED = "seed"
    SAFETY_TOLERANCE = "safety_tolerance"
    OUTPUT_FORMAT = "output_format"
    STEPS = "steps"
    GUIDANCE = "guidance"


class ImageGenerationParameters(Parameters):
    """Parameters for image generation."""

    aspect_ratio: str | None
    num_images: int | None
    partial_images: int | None
    quality: str | None
    watermark: bool | None
    reference_images: list[ImageArtifact] | None
    prompt_upsampling: bool | None
    seed: int | None
    safety_tolerance: int | None
    output_format: str | None
    steps: int | None
    guidance: float | None
