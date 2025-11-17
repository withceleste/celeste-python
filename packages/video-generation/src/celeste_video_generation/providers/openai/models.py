"""OpenAI models for video generation."""

from celeste import Model, Provider
from celeste.constraints import Choice, ImageConstraint
from celeste.mime_types import ImageMimeType
from celeste_video_generation.parameters import VideoGenerationParameter

MODELS: list[Model] = [
    Model(
        id="sora-2",
        provider=Provider.OPENAI,
        display_name="Sora 2",
        parameter_constraints={
            VideoGenerationParameter.DURATION: Choice(options=["4", "8", "12"]),
            VideoGenerationParameter.ASPECT_RATIO: Choice(options=["16:9", "9:16"]),
            VideoGenerationParameter.RESOLUTION: Choice(options=["720p"]),
        },
    ),
    Model(
        id="sora-2-pro",
        provider=Provider.OPENAI,
        display_name="Sora 2 Pro",
        parameter_constraints={
            VideoGenerationParameter.DURATION: Choice(options=["4", "8", "12"]),
            VideoGenerationParameter.ASPECT_RATIO: Choice(options=["16:9", "9:16"]),
            VideoGenerationParameter.RESOLUTION: Choice(options=["720p"]),
            VideoGenerationParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=[
                    ImageMimeType.JPEG,
                    ImageMimeType.PNG,
                    ImageMimeType.WEBP,
                ],
            ),
        },
    ),
]
