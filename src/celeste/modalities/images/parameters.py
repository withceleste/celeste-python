"""Parameters for images modality."""

from enum import StrEnum

from celeste.artifacts import ImageArtifact
from celeste.parameters import Parameters


class ImageParameter(StrEnum):
    """Parameter names for images modality."""

    ASPECT_RATIO = "aspect_ratio"
    NUM_IMAGES = "num_images"
    PARTIAL_IMAGES = "partial_images"
    QUALITY = "quality"
    WATERMARK = "watermark"
    REFERENCE_IMAGES = "reference_images"
    PROMPT_UPSAMPLING = "prompt_upsampling"
    NEGATIVE_PROMPT = "negative_prompt"
    SEED = "seed"
    SAFETY_TOLERANCE = "safety_tolerance"
    OUTPUT_FORMAT = "output_format"
    STEPS = "steps"
    GUIDANCE = "guidance"
    MASK = "mask"


class ImageParameters(Parameters):
    """Parameters for images operations."""

    aspect_ratio: str
    num_images: int
    partial_images: int
    quality: str
    watermark: bool
    reference_images: list[ImageArtifact]
    prompt_upsampling: bool
    negative_prompt: str
    seed: int
    safety_tolerance: int
    output_format: str
    steps: int
    guidance: float
    mask: ImageArtifact


__all__ = [
    "ImageParameter",
    "ImageParameters",
]
