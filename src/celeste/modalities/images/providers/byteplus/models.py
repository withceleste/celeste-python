"""BytePlus models for images modality."""

from celeste.constraints import Bool, Choice, Dimensions, ImagesConstraint
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import ImageParameter

MODELS: list[Model] = [
    Model(
        id="seedream-4-0-250828",
        provider=Provider.BYTEPLUS,
        display_name="Seedream 4.0",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=1280 * 720,  # 921,600
                max_pixels=4096 * 4096,  # 16,777,216
                min_aspect_ratio=1 / 16,
                max_aspect_ratio=16,
                presets={
                    "1K 1:1": "1024x1024",
                    "1K 3:4": "864x1152",
                    "1K 4:3": "1152x864",
                    "1K 16:9": "1312x736",
                    "1K 9:16": "736x1312",
                    "1K 2:3": "832x1248",
                    "1K 3:2": "1248x832",
                    "1K 21:9": "1568x672",
                    "2K 1:1": "2048x2048",
                    "2K 3:4": "1728x2304",
                    "2K 4:3": "2304x1728",
                    "2K 16:9": "2848x1600",
                    "2K 9:16": "1600x2848",
                    "2K 3:2": "2496x1664",
                    "2K 2:3": "1664x2496",
                    "2K 21:9": "3136x1344",
                    "4K 1:1": "4096x4096",
                    "4K 3:4": "3520x4704",
                    "4K 4:3": "4704x3520",
                    "4K 16:9": "5504x3040",
                    "4K 9:16": "3040x5504",
                    "4K 2:3": "3328x4992",
                    "4K 3:2": "4992x3328",
                    "4K 21:9": "6240x2656",
                },
            ),
            ImageParameter.QUALITY: Choice(options=["1K", "2K", "4K"]),
            ImageParameter.WATERMARK: Bool(),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=14),
        },
    ),
    Model(
        id="seedream-4-5-251128",
        provider=Provider.BYTEPLUS,
        display_name="Seedream 4.5",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=2560 * 1440,  # 3,686,400
                max_pixels=4096 * 4096,  # 16,777,216
                min_aspect_ratio=1 / 16,
                max_aspect_ratio=16,
                presets={
                    "2K 1:1": "2048x2048",
                    "2K 3:4": "1728x2304",
                    "2K 4:3": "2304x1728",
                    "2K 16:9": "2848x1600",
                    "2K 9:16": "1600x2848",
                    "2K 3:2": "2496x1664",
                    "2K 2:3": "1664x2496",
                    "2K 21:9": "3136x1344",
                    "4K 1:1": "4096x4096",
                    "4K 3:4": "3520x4704",
                    "4K 4:3": "4704x3520",
                    "4K 16:9": "5504x3040",
                    "4K 9:16": "3040x5504",
                    "4K 2:3": "3328x4992",
                    "4K 3:2": "4992x3328",
                    "4K 21:9": "6240x2656",
                },
            ),
            ImageParameter.QUALITY: Choice(options=["2K", "4K"]),
            ImageParameter.WATERMARK: Bool(),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=14),
        },
    ),
    Model(
        id="seedream-5-0-260128",
        provider=Provider.BYTEPLUS,
        display_name="Seedream 5.0 Lite",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=2560 * 1440,  # 3,686,400
                max_pixels=4096 * 4096,  # 16,777,216
                min_aspect_ratio=1 / 16,
                max_aspect_ratio=16,
                presets={
                    "2K 1:1": "2048x2048",
                    "2K 3:4": "1728x2304",
                    "2K 4:3": "2304x1728",
                    "2K 16:9": "2848x1600",
                    "2K 9:16": "1600x2848",
                    "2K 3:2": "2496x1664",
                    "2K 2:3": "1664x2496",
                    "2K 21:9": "3136x1344",
                    "3K 1:1": "3072x3072",
                    "3K 3:4": "2592x3456",
                    "3K 4:3": "3456x2592",
                    "3K 16:9": "4096x2304",
                    "3K 9:16": "2304x4096",
                    "3K 2:3": "2496x3744",
                    "3K 3:2": "3744x2496",
                    "3K 21:9": "4704x2016",
                    "4K 1:1": "4096x4096",
                    "4K 3:4": "3520x4704",
                    "4K 4:3": "4704x3520",
                    "4K 16:9": "5504x3040",
                    "4K 9:16": "3040x5504",
                    "4K 2:3": "3328x4992",
                    "4K 3:2": "4992x3328",
                    "4K 21:9": "6240x2656",
                },
            ),
            ImageParameter.QUALITY: Choice(options=["2K", "3K", "4K"]),
            ImageParameter.WATERMARK: Bool(),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png"]),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=14),
        },
    ),
    Model(
        id="dola-seedream-5-0-pro-260628",
        provider=Provider.BYTEPLUS,
        display_name="Seedream 5.0 Pro",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=False,
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=1280 * 720,  # 921,600
                max_pixels=4_624_220,
                min_aspect_ratio=1 / 16,
                max_aspect_ratio=16,
                multiple_of=16,
                presets={
                    "1K 1:1": "1024x1024",
                    "1K 4:3": "1152x864",
                    "1K 3:4": "864x1152",
                    "1K 16:9": "1424x800",
                    "1K 9:16": "800x1424",
                    "1K 3:2": "1248x832",
                    "1K 2:3": "832x1248",
                    "1K 21:9": "1568x672",
                    "1.5K 1:1": "1536x1536",
                    "1.5K 4:3": "1792x1344",
                    "1.5K 3:4": "1344x1792",
                    "1.5K 16:9": "2048x1152",
                    "1.5K 9:16": "1152x2048",
                    "1.5K 3:2": "1872x1248",
                    "1.5K 2:3": "1248x1872",
                    "1.5K 21:9": "2352x1008",
                    "2K 1:1": "2048x2048",
                    "2K 4:3": "2368x1776",
                    "2K 3:4": "1776x2368",
                    "2K 16:9": "2816x1584",
                    "2K 9:16": "1584x2816",
                    "2K 3:2": "2496x1664",
                    "2K 2:3": "1664x2496",
                    "2K 21:9": "3136x1344",
                },
            ),
            ImageParameter.QUALITY: Choice(options=["1K", "1.5K", "2K"]),
            ImageParameter.WATERMARK: Bool(),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["jpeg", "png"]),
            ImageParameter.BACKGROUND: Choice(options=["opaque", "transparent"]),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=10),
        },
    ),
]

MODELS.append(
    next(model for model in MODELS if model.id == "seedream-5-0-260128").model_copy(
        update={
            "id": "seedream-5-0-lite-260128",
            "display_name": "Seedream 5.0 Lite (alias)",
        }
    )
)
