"""ByteDance models for image generation."""

from celeste import Model, Provider
from celeste.constraints import Bool, Choice
from celeste_image_generation.constraints import Dimensions
from celeste_image_generation.parameters import ImageGenerationParameter

MODELS: list[Model] = [
    Model(
        id="seedream-4-0-250828",
        provider=Provider.BYTEDANCE,
        display_name="Seedream 4.0",
        parameter_constraints={
            ImageGenerationParameter.ASPECT_RATIO: Dimensions(
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
            ImageGenerationParameter.QUALITY: Choice(options=["1K", "2K", "4K"]),
            ImageGenerationParameter.WATERMARK: Bool(),
        },
    ),
]
