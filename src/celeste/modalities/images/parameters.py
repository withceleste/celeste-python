"""Parameters for images modality."""

from enum import StrEnum
from typing import Annotated

from pydantic import Field

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
    THINKING_LEVEL = "thinking_level"
    BACKGROUND = "background"
    OUTPUT_COMPRESSION = "output_compression"
    OUTPUT_WIDTH = "output_width"
    OUTPUT_HEIGHT = "output_height"
    CROP_TO_FILL = "crop_to_fill"
    FACE_ENHANCEMENT = "face_enhancement"
    FACE_ENHANCEMENT_STRENGTH = "face_enhancement_strength"
    FACE_ENHANCEMENT_CREATIVITY = "face_enhancement_creativity"
    SUBJECT_DETECTION = "subject_detection"
    SHARPEN = "sharpen"
    DENOISE = "denoise"
    STRENGTH = "strength"
    FIX_COMPRESSION = "fix_compression"
    RECOVERY_STRENGTH = "recovery_strength"
    OPACITY = "opacity"
    DEBLUR_STRENGTH = "deblur_strength"
    DETAIL_STRENGTH = "detail_strength"
    DENOISE_STRENGTH = "denoise_strength"
    DECOMPRESSION_STRENGTH = "decompression_strength"


class ImageParameters(Parameters, total=False):
    """Parameters for images operations."""

    aspect_ratio: Annotated[
        str, Field(description="Output image dimensions or aspect ratio.")
    ]
    num_images: Annotated[int, Field(description="How many images to return.")]
    partial_images: Annotated[
        int, Field(description="Number of progressive partial outputs to stream.")
    ]
    quality: Annotated[str, Field(description="Output quality tier.")]
    watermark: Annotated[bool, Field(description="Embed a watermark in the output.")]
    reference_images: Annotated[
        list[ImageArtifact],
        Field(description="Additional images for composition or style reference."),
    ]
    prompt_upsampling: Annotated[
        bool, Field(description="Let the model rewrite the prompt for better results.")
    ]
    negative_prompt: Annotated[
        str, Field(description="Concepts to avoid in the output.")
    ]
    seed: Annotated[int, Field(description="Seed for deterministic output.")]
    safety_tolerance: Annotated[
        int | str,
        Field(
            description="Safety filter threshold — integer tier (BFL) or preset name (OpenAI 'auto'/'low')."
        ),
    ]
    output_format: Annotated[str, Field(description="Output file format.")]
    steps: Annotated[int, Field(description="Number of denoising steps.")]
    guidance: Annotated[float, Field(description="Prompt-adherence strength.")]
    mask: Annotated[
        ImageArtifact, Field(description="Mask image for inpainting a region.")
    ]
    thinking_level: Annotated[str, Field(description="Model reasoning depth.")]
    background: Annotated[
        str, Field(description="Background handling (e.g. transparent, opaque, auto).")
    ]
    output_compression: Annotated[
        int, Field(description="Output compression level (0-100) for jpeg/webp.")
    ]
    output_width: Annotated[int, Field(description="Target output width in pixels.")]
    output_height: Annotated[int, Field(description="Target output height in pixels.")]
    crop_to_fill: Annotated[
        bool, Field(description="Crop output to fill the requested dimensions.")
    ]
    face_enhancement: Annotated[
        bool, Field(description="Apply face recovery enhancement.")
    ]
    face_enhancement_strength: Annotated[
        float, Field(description="Strength of face recovery (0-1).")
    ]
    face_enhancement_creativity: Annotated[
        float, Field(description="Creative vs realistic face recovery (0-1).")
    ]
    subject_detection: Annotated[
        str,
        Field(description="Where enhancements apply: foreground, background, or all."),
    ]
    sharpen: Annotated[float, Field(description="Sharpening strength (0-1).")]
    denoise: Annotated[float, Field(description="Denoise strength (0-1).")]
    strength: Annotated[float, Field(description="Model enhancement strength.")]
    fix_compression: Annotated[
        float, Field(description="Compression-artifact cleanup strength (0-1).")
    ]
    recovery_strength: Annotated[
        float, Field(description="Detail recovery strength for fidelity models.")
    ]
    opacity: Annotated[
        float, Field(description="Blend opacity for enhancement output.")
    ]
    deblur_strength: Annotated[float, Field(description="Deblur strength (0-1).")]
    detail_strength: Annotated[
        float, Field(description="Facial detail enhancement strength.")
    ]
    denoise_strength: Annotated[
        float, Field(description="Model-specific denoise strength (0-1).")
    ]
    decompression_strength: Annotated[
        float, Field(description="Model-specific decompression strength (0-1).")
    ]


__all__ = [
    "ImageParameter",
    "ImageParameters",
]
