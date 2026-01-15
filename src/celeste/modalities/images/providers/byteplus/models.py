"""BytePlus models for images modality."""

from celeste.constraints import Bool, Choice, Dimensions
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import ImageParameter

MODELS: list[Model] = [
    Model(
        id="seedream-4-0-250828",
        provider=Provider.BYTEPLUS,
        display_name="Seedream 4.0",
        operations={Modality.IMAGES: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=1280 * 720,  # 921,600
                max_pixels=4096 * 4096,  # 16,777,216
                min_aspect_ratio=1 / 16,  # 0.0625
                max_aspect_ratio=16,
                presets={
                    "Square 2K": "2048x2048",
                    "Square 4K": "4096x4096",
                    "HD 16:9": "1920x1080",
                    "2K 16:9": "2560x1440",
                    "4K 16:9": "3840x2160",
                    "Portrait HD": "1080x1920",
                    "Portrait 2K": "1440x2560",
                    "Ultra-wide 21:9": "3024x1296",
                },
            ),
            ImageParameter.QUALITY: Choice(options=["1K", "2K", "4K"]),
            ImageParameter.WATERMARK: Bool(),
        },
    ),
    Model(
        id="seedream-4-5-251128",
        provider=Provider.BYTEPLUS,
        display_name="Seedream 4.5",
        operations={Modality.IMAGES: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Dimensions(
                min_pixels=2560 * 1440,  # 3,686,400
                max_pixels=4096 * 4096,  # 16,777,216
                min_aspect_ratio=1 / 16,  # 0.0625
                max_aspect_ratio=16,
                presets={
                    "Square 2K": "2048x2048",
                    "Square 4K": "4096x4096",
                    "HD 16:9": "1920x1080",
                    "2K 16:9": "2560x1440",
                    "4K 16:9": "3840x2160",
                    "Portrait HD": "1080x1920",
                    "Portrait 2K": "1440x2560",
                    "Ultra-wide 21:9": "3024x1296",
                },
            ),
            ImageParameter.QUALITY: Choice(options=["2K", "4K"]),
            ImageParameter.WATERMARK: Bool(),
        },
    ),
]
