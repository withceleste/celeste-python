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

# FLUX 3 models (images list, native aspect_ratio)
BFL_FLUX3_MODELS: list[Model] = [
    Model(
        id="flux-3-image",
        provider=Provider.BFL,
        display_name="FLUX 3 Image",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Choice(
                options=[
                    "21:9",
                    "2:1",
                    "16:9",
                    "3:2",
                    "7:5",
                    "4:3",
                    "5:4",
                    "1:1",
                    "4:5",
                    "3:4",
                    "5:7",
                    "2:3",
                    "9:16",
                    "1:2",
                    "9:21",
                    "auto",
                ]
            ),
            ImageParameter.QUALITY: Choice(options=["768sq", "1k", "1.5k", "2k", "4k"]),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=10),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=7),
            ImageParameter.GROUNDING: Bool(),
        },
    ),
    Model(
        id="flux-3-image-klein",
        provider=Provider.BFL,
        display_name="FLUX 3 Image Klein",
        operations={Modality.IMAGES: {Operation.GENERATE}},
        parameter_constraints={
            ImageParameter.QUALITY: Choice(options=["768sq", "1k", "1.5k", "2k", "4k"]),
            ImageParameter.SEED: Range(min=0, max=4294967295),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=7),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png"]),
            ImageParameter.STEPS: Range(min=1, max=16),
        },
    ),
]

# FLUX.2 models (input_image, input_image_2, ...; width and height)
BFL_FLUX2_MODELS: list[Model] = [
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
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=8),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Int(
                description="Standard levels are 0-5; higher levels require BFL authorization."
            ),
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
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=8),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Int(
                description="Standard levels are 0-5; higher levels require BFL authorization."
            ),
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
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=8),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Int(
                description="Standard levels are 0-5; higher levels require BFL authorization."
            ),
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
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=5),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Int(
                description="Standard levels are 0-5; higher levels require BFL authorization."
            ),
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
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=5),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Int(
                description="Standard levels are 0-5; higher levels require BFL authorization."
            ),
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
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=5),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Int(
                description="Standard levels are 0-5; higher levels require BFL authorization."
            ),
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
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=8),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Int(
                description="Standard levels are 0-5; higher levels require BFL authorization."
            ),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
            ImageParameter.STEPS: Range(min=1, max=50),
            ImageParameter.GUIDANCE: Range(min=1.5, max=10.0),
        },
    ),
]

# FLUX.1 Kontext models (input_image, input_image_2, ...; native aspect_ratio)
BFL_KONTEXT_MODELS: list[Model] = [
    Model(
        id="flux-kontext-max",
        provider=Provider.BFL,
        display_name="FLUX.1 Kontext [max]",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Str(
                description="Native width:height ratio, such as 16:9; BFL determines output dimensions."
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
                description="Native width:height ratio, such as 16:9; BFL determines output dimensions."
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
]

# FLUX.1 models (image_prompt)
BFL_FLUX1_MODELS: list[Model] = [
    Model(
        id="flux-pro-1.1-ultra",
        provider=Provider.BFL,
        display_name="FLUX1.1 [pro] Ultra",
        operations={Modality.IMAGES: {Operation.GENERATE}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Str(
                description="Native width:height ratio, such as 16:9; BFL determines output dimensions."
            ),
            ImageParameter.PROMPT_UPSAMPLING: Bool(),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=1),
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
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=1),
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
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=1),
            ImageParameter.SEED: Int(),
            ImageParameter.SAFETY_TOLERANCE: Range(min=0, max=6),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png", "webp"]),
            ImageParameter.STEPS: Range(min=1, max=50),
            ImageParameter.GUIDANCE: Range(min=1.5, max=5.0),
        },
    ),
]

# Unified model list for registration
MODELS: list[Model] = [
    *BFL_FLUX3_MODELS,
    *BFL_FLUX2_MODELS,
    *BFL_KONTEXT_MODELS,
    *BFL_FLUX1_MODELS,
]

# FLUX.2 models that take disable_pup (inverted); flux-2-flex takes prompt_upsampling.
BFL_FLUX2_DISABLE_PUP_MODELS = frozenset(
    {
        "flux-2-max",
        "flux-2-pro",
        "flux-2-pro-preview",
    }
)

# FLUX.2 [klein] models have no prompt upsampling field; the value is dropped.
BFL_FLUX2_KLEIN_MODELS = frozenset(
    {
        "flux-2-klein-4b",
        "flux-2-klein-9b",
        "flux-2-klein-9b-preview",
    }
)

# FLUX.1 models that take a native aspect_ratio; the others take width and height.
BFL_FLUX1_ASPECT_RATIO_MODELS = frozenset(
    {
        "flux-pro-1.1-ultra",
    }
)

__all__ = [
    "BFL_FLUX1_MODELS",
    "BFL_FLUX2_MODELS",
    "BFL_FLUX3_MODELS",
    "BFL_KONTEXT_MODELS",
    "MODELS",
]
