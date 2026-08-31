"""BFL (Black Forest Labs) models for images modality."""

from celeste.constraints import (
    Bool,
    Choice,
    Constraint,
    Dimensions,
    ImagesConstraint,
    Int,
    Range,
    Str,
)
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import ImageParameter

_FLUX_2_DIMENSIONS = Dimensions(
    min_pixels=64 * 64,
    max_pixels=2048 * 2048,
    # Ratios follow only from the per-axis minimum and total pixel maximum.
    min_aspect_ratio=1 / 1024,
    max_aspect_ratio=1024,
    min_dimension=64,
    multiple_of=16,
    presets={
        "Square 1K": "1024x1024",
        "Square 2K": "2048x2048",
        "HD 16:9": "1920x1088",
        "Portrait HD": "1088x1920",
        "4:3": "1280x960",
        "3:4": "960x1280",
        "Ultra-wide 21:9": "1920x832",
        "Portrait 9:21": "832x1920",
    },
)
_LEGACY_DIMENSIONS = Dimensions(
    min_pixels=256 * 256,
    max_pixels=1440 * 1440,
    min_aspect_ratio=256 / 1440,
    max_aspect_ratio=1440 / 256,
    min_dimension=256,
    max_dimension=1440,
    multiple_of=32,
    presets={"Square": "1024x1024", "Landscape": "1024x768", "Portrait": "768x1024"},
)
_LEGACY_CONSTRAINTS: dict[str, Constraint] = {
    ImageParameter.PROMPT_UPSAMPLING: Bool(),
    ImageParameter.SEED: Int(),
    ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=6, step=1),
    ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
}
_ASPECT_RATIO = Str(description="Aspect ratio from 3:7 to 7:3, for example 16:9.")

MODELS: list[Model] = [
    Model(
        id="flux-2-max",
        provider=Provider.BFL,
        display_name="FLUX.2 [max]",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: _FLUX_2_DIMENSIONS,
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=7),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5, step=1),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-2-pro",
        provider=Provider.BFL,
        display_name="FLUX.2 [pro]",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: _FLUX_2_DIMENSIONS,
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=7),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5, step=1),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-2-pro-preview",
        provider=Provider.BFL,
        display_name="FLUX.2 [pro] Preview",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: _FLUX_2_DIMENSIONS,
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=7),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5, step=1),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-2-klein-4b",
        provider=Provider.BFL,
        display_name="FLUX.2 [klein] 4B",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: _FLUX_2_DIMENSIONS,
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=3),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5, step=1),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-2-klein-9b",
        provider=Provider.BFL,
        display_name="FLUX.2 [klein] 9B",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: _FLUX_2_DIMENSIONS,
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=3),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5, step=1),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-2-klein-9b-preview",
        provider=Provider.BFL,
        display_name="FLUX.2 [klein] 9B Preview",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: _FLUX_2_DIMENSIONS,
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=3),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5, step=1),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-2-flex",
        provider=Provider.BFL,
        display_name="FLUX.2 [flex]",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: _FLUX_2_DIMENSIONS,
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=7),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5, step=1),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
            ImageParameter.STEPS: Range(min=1, max=50, step=1),
            ImageParameter.GUIDANCE: Range(min=1.5, max=10.0),
        },
    ),
    Model(
        id="flux-kontext-max",
        provider=Provider.BFL,
        display_name="FLUX.1 Kontext [max]",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            **_LEGACY_CONSTRAINTS,
            ImageParameter.ASPECT_RATIO: _ASPECT_RATIO,
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(
                max_count=3, description="Experimental additional reference images."
            ),
        },
    ),
    Model(
        id="flux-kontext-pro",
        provider=Provider.BFL,
        display_name="FLUX.1 Kontext [pro]",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            **_LEGACY_CONSTRAINTS,
            ImageParameter.ASPECT_RATIO: _ASPECT_RATIO,
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(
                max_count=3, description="Experimental additional reference images."
            ),
        },
    ),
    Model(
        id="flux-pro-1.1-ultra",
        provider=Provider.BFL,
        display_name="FLUX1.1 [pro] Ultra",
        operations={Modality.IMAGES: {Operation.GENERATE}},
        parameter_constraints={
            **_LEGACY_CONSTRAINTS,
            ImageParameter.ASPECT_RATIO: _ASPECT_RATIO,
        },
    ),
    Model(
        id="flux-pro-1.1",
        provider=Provider.BFL,
        display_name="FLUX1.1 [pro]",
        operations={Modality.IMAGES: {Operation.GENERATE}},
        parameter_constraints={
            **_LEGACY_CONSTRAINTS,
            ImageParameter.ASPECT_RATIO: _LEGACY_DIMENSIONS,
        },
    ),
    Model(
        id="flux-dev",
        provider=Provider.BFL,
        display_name="FLUX.1 [dev]",
        operations={Modality.IMAGES: {Operation.GENERATE}},
        parameter_constraints={
            **_LEGACY_CONSTRAINTS,
            ImageParameter.ASPECT_RATIO: _LEGACY_DIMENSIONS,
            ImageParameter.STEPS: Range(min=1, max=50, step=1),
            ImageParameter.GUIDANCE: Range(min=1.5, max=5.0),
        },
    ),
]

__all__ = ["MODELS"]
