"""BFL (Black Forest Labs) models for images modality."""

from celeste.constraints import (
    Bool,
    Choice,
    Dimensions,
    ImagesConstraint,
    Int,
    Range,
    Str,
)
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import ImageParameter

MODELS: list[Model] = [
    Model(
        id="flux-2-max",
        provider=Provider.BFL,
        display_name="FLUX.2 [max]",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=64 * 64,  # 4,096
                max_pixels=2048 * 2048,  # 4,194,304 (4MP)
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
            ),
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=8),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-2-pro",
        provider=Provider.BFL,
        display_name="FLUX.2 [pro]",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=64 * 64,  # 4,096
                max_pixels=2048 * 2048,  # 4,194,304 (4MP)
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
            ),
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=8),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-2-pro-preview",
        provider=Provider.BFL,
        display_name="FLUX.2 [pro] Preview",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=64 * 64,
                max_pixels=2048 * 2048,
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
            ),
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=8),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-2-klein-4b",
        provider=Provider.BFL,
        display_name="FLUX.2 [klein] 4B",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=64 * 64,
                max_pixels=2048 * 2048,
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
            ),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=4),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-2-klein-9b",
        provider=Provider.BFL,
        display_name="FLUX.2 [klein] 9B",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=64 * 64,
                max_pixels=2048 * 2048,
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
            ),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=4),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-2-klein-9b-preview",
        provider=Provider.BFL,
        display_name="FLUX.2 [klein] 9B Preview",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=64 * 64,
                max_pixels=2048 * 2048,
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
            ),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=4),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-2-flex",
        provider=Provider.BFL,
        display_name="FLUX.2 [flex]",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=64 * 64,  # 4,096
                max_pixels=2048 * 2048,  # 4,194,304 (4MP)
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
            ),
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=8),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
            ImageParameter.STEPS: Range(min=1, max=50),
            ImageParameter.GUIDANCE: Range(min=1.5, max=10.0),
        },
    ),
    Model(
        id="flux-kontext-max",
        provider=Provider.BFL,
        display_name="FLUX.1 Kontext [max]",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Str(
                description="Width:height ratio between 9:21 and 21:9"
            ),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(
                max_count=4,
                description="Experimental multi-reference inputs, including the primary edit image",
            ),
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=6),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-kontext-pro",
        provider=Provider.BFL,
        display_name="FLUX.1 Kontext [pro]",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Str(
                description="Width:height ratio between 9:21 and 21:9"
            ),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(
                max_count=4,
                description="Experimental multi-reference inputs, including the primary edit image",
            ),
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=6),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-pro-1.1-ultra",
        provider=Provider.BFL,
        display_name="FLUX1.1 [pro] Ultra",
        operations={Modality.IMAGES: {Operation.GENERATE}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Str(
                description="Width:height ratio between 9:21 and 21:9"
            ),
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=6),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-pro-1.1",
        provider=Provider.BFL,
        display_name="FLUX1.1 [pro]",
        operations={Modality.IMAGES: {Operation.GENERATE}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=256 * 256,
                max_pixels=1440 * 1440,
                min_aspect_ratio=256 / 1440,
                max_aspect_ratio=1440 / 256,
                min_dimension=256,
                max_dimension=1440,
                multiple_of=32,
            ),
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=6),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
        },
    ),
    Model(
        id="flux-dev",
        provider=Provider.BFL,
        display_name="FLUX.1 [dev]",
        operations={Modality.IMAGES: {Operation.GENERATE}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=256 * 256,
                max_pixels=1440 * 1440,
                min_aspect_ratio=256 / 1440,
                max_aspect_ratio=1440 / 256,
                min_dimension=256,
                max_dimension=1440,
                multiple_of=32,
            ),
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=6),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
            ImageParameter.STEPS: Range(min=1, max=50),
            ImageParameter.GUIDANCE: Range(min=1.5, max=5.0),
        },
    ),
]

__all__ = ["MODELS"]
