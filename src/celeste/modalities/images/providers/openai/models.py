"""OpenAI models for images modality."""

from celeste.constraints import (
    Choice,
    Dimensions,
    ImageConstraint,
    ImagesConstraint,
    Range,
)
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import ImageParameter

MODELS: list[Model] = [
    Model(
        id="gpt-image-1-mini",
        provider=Provider.OPENAI,
        display_name="GPT Image 1 Mini",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageParameter.ASPECT_RATIO: Choice(
                options=["1024x1024", "1024x1536", "1536x1024", "auto"]
            ),
            ImageParameter.QUALITY: Choice(options=["low", "medium", "high", "auto"]),
            ImageParameter.NUM_IMAGES: Range(min=1, max=10),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["png", "jpeg", "webp"]),
            ImageParameter.BACKGROUND: Choice(
                options=["transparent", "opaque", "auto"]
            ),
            ImageParameter.SAFETY_TOLERANCE: Choice(options=["auto", "low"]),
            ImageParameter.OUTPUT_COMPRESSION: Range(min=0, max=100),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=16),
            ImageParameter.MASK: ImageConstraint(),
        },
    ),
    Model(
        id="gpt-image-1.5",
        provider=Provider.OPENAI,
        display_name="GPT Image 1.5",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageParameter.ASPECT_RATIO: Choice(
                options=["1024x1024", "1536x1024", "1024x1536", "auto"]
            ),
            ImageParameter.QUALITY: Choice(options=["low", "medium", "high", "auto"]),
            ImageParameter.NUM_IMAGES: Range(min=1, max=10),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["png", "jpeg", "webp"]),
            ImageParameter.BACKGROUND: Choice(
                options=["transparent", "opaque", "auto"]
            ),
            ImageParameter.SAFETY_TOLERANCE: Choice(options=["auto", "low"]),
            ImageParameter.OUTPUT_COMPRESSION: Range(min=0, max=100),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=16),
            ImageParameter.MASK: ImageConstraint(),
        },
    ),
    Model(
        id="gpt-image-2",
        provider=Provider.OPENAI,
        display_name="GPT Image 2",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=655_360,
                max_pixels=3840 * 2160,  # 8,294,400
                min_aspect_ratio=1 / 3,
                max_aspect_ratio=3,
                multiple_of=16,
                max_dimension=3840,
                presets={
                    "Square": "1024x1024",
                    "Landscape": "1536x1024",
                    "Portrait": "1024x1536",
                    "Square 2K": "2048x2048",
                    "Landscape 2K": "2048x1152",
                    "Landscape 4K": "3840x2160",
                    "Portrait 4K": "2160x3840",
                },
            ),
            ImageParameter.QUALITY: Choice(options=["low", "medium", "high", "auto"]),
            ImageParameter.NUM_IMAGES: Range(min=1, max=10),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["png", "jpeg", "webp"]),
            ImageParameter.BACKGROUND: Choice(
                options=["transparent", "opaque", "auto"]
            ),
            ImageParameter.SAFETY_TOLERANCE: Choice(options=["auto", "low"]),
            ImageParameter.OUTPUT_COMPRESSION: Range(min=0, max=100),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=16),
            ImageParameter.MASK: ImageConstraint(),
        },
    ),
    Model(
        id="gpt-image-2.5-flare",
        provider=Provider.OPENAI,
        display_name="GPT Image 2.5 Flare",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=655_360,
                max_pixels=3840 * 2160,  # 8,294,400
                min_aspect_ratio=1 / 3,
                max_aspect_ratio=3,
                multiple_of=16,
                max_dimension=3840,
                presets={
                    "Square": "1024x1024",
                    "Landscape": "1536x1024",
                    "Portrait": "1024x1536",
                    "Square 2K": "2048x2048",
                    "Landscape 2K": "2048x1152",
                    "Landscape 4K": "3840x2160",
                    "Portrait 4K": "2160x3840",
                },
            ),
            ImageParameter.QUALITY: Choice(
                options=["low", "medium", "high", "xhigh", "max", "auto"]
            ),
            ImageParameter.NUM_IMAGES: Range(min=1, max=10),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["png", "jpeg", "webp"]),
            ImageParameter.BACKGROUND: Choice(
                options=["transparent", "opaque", "auto"]
            ),
            ImageParameter.SAFETY_TOLERANCE: Choice(options=["auto", "low"]),
            ImageParameter.OUTPUT_COMPRESSION: Range(min=0, max=100),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=16),
            ImageParameter.MASK: ImageConstraint(),
        },
    ),
    Model(
        id="gpt-image-2.6-flare",
        provider=Provider.OPENAI,
        display_name="GPT Image 2.6 Flare",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageParameter.ASPECT_RATIO: Choice(
                options=["1024x1024", "1536x1024", "1024x1536", "auto"]
            ),
            ImageParameter.QUALITY: Choice(options=["low", "medium", "high", "auto"]),
            ImageParameter.NUM_IMAGES: Range(min=1, max=10),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["png", "jpeg", "webp"]),
            ImageParameter.BACKGROUND: Choice(
                options=["transparent", "opaque", "auto"]
            ),
            ImageParameter.SAFETY_TOLERANCE: Choice(options=["auto", "low"]),
            ImageParameter.OUTPUT_COMPRESSION: Range(min=0, max=100),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=16),
            ImageParameter.MASK: ImageConstraint(),
        },
    ),
    Model(
        id="gpt-image-2.5-sunburst",
        provider=Provider.OPENAI,
        display_name="GPT Image 2.5 Sunburst",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=655_360,
                max_pixels=3840 * 2160,  # 8,294,400
                min_aspect_ratio=1 / 3,
                max_aspect_ratio=3,
                multiple_of=16,
                max_dimension=3840,
                presets={
                    "Square": "1024x1024",
                    "Landscape": "1536x1024",
                    "Portrait": "1024x1536",
                    "Square 2K": "2048x2048",
                    "Landscape 2K": "2048x1152",
                    "Landscape 4K": "3840x2160",
                    "Portrait 4K": "2160x3840",
                },
            ),
            ImageParameter.QUALITY: Choice(
                options=["low", "medium", "high", "xhigh", "max", "auto"]
            ),
            ImageParameter.NUM_IMAGES: Range(min=1, max=10),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["png", "jpeg", "webp"]),
            ImageParameter.BACKGROUND: Choice(
                options=["transparent", "opaque", "auto"]
            ),
            ImageParameter.SAFETY_TOLERANCE: Choice(options=["auto", "low"]),
            ImageParameter.OUTPUT_COMPRESSION: Range(min=0, max=100),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=16),
            ImageParameter.MASK: ImageConstraint(),
        },
    ),
    Model(
        id="gpt-image-2.6-sunburst",
        provider=Provider.OPENAI,
        display_name="GPT Image 2.6 Sunburst",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageParameter.ASPECT_RATIO: Choice(
                options=["1024x1024", "1536x1024", "1024x1536", "auto"]
            ),
            ImageParameter.QUALITY: Choice(options=["low", "medium", "high", "auto"]),
            ImageParameter.NUM_IMAGES: Range(min=1, max=10),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["png", "jpeg", "webp"]),
            ImageParameter.BACKGROUND: Choice(
                options=["transparent", "opaque", "auto"]
            ),
            ImageParameter.SAFETY_TOLERANCE: Choice(options=["auto", "low"]),
            ImageParameter.OUTPUT_COMPRESSION: Range(min=0, max=100),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=16),
            ImageParameter.MASK: ImageConstraint(),
        },
    ),
]
