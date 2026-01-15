"""BFL (Black Forest Labs) models for images modality."""

from celeste.constraints import Choice, Dimensions, ImagesConstraint, Int, Range
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
                min_aspect_ratio=9 / 21,  # ~0.429
                max_aspect_ratio=21 / 9,  # ~2.333
                presets={
                    "Square 1K": "1024x1024",
                    "Square 2K": "2048x2048",
                    "HD 16:9": "1920x1080",
                    "Portrait HD": "1080x1920",
                    "4:3": "1280x960",
                    "3:4": "960x1280",
                    "Ultra-wide 21:9": "1920x832",
                    "Portrait 9:21": "832x1920",
                },
            ),
            # Note: flux-2-max always upsamples prompts (no prompt_upsampling parameter)
            # Includes grounding search for real-time information integration
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=7),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png"]),
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
                min_aspect_ratio=9 / 21,  # ~0.429
                max_aspect_ratio=21 / 9,  # ~2.333
                presets={
                    "Square 1K": "1024x1024",
                    "Square 2K": "2048x2048",
                    "HD 16:9": "1920x1080",
                    "Portrait HD": "1080x1920",
                    "4:3": "1280x960",
                    "3:4": "960x1280",
                    "Ultra-wide 21:9": "1920x832",
                    "Portrait 9:21": "832x1920",
                },
            ),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=7),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png"]),
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
                min_aspect_ratio=9 / 21,  # ~0.429
                max_aspect_ratio=21 / 9,  # ~2.333
                presets={
                    "Square 1K": "1024x1024",
                    "Square 2K": "2048x2048",
                    "HD 16:9": "1920x1080",
                    "Portrait HD": "1080x1920",
                    "4:3": "1280x960",
                    "3:4": "960x1280",
                    "Ultra-wide 21:9": "1920x832",
                    "Portrait 9:21": "832x1920",
                },
            ),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=9),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=5),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png"]),
            ImageParameter.STEPS: Range(min=1, max=50),
            ImageParameter.GUIDANCE: Range(min=1.5, max=10.0),
        },
    ),
]

__all__ = ["MODELS"]
