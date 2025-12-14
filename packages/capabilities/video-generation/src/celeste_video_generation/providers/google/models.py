"""Google models for video generation."""

from celeste import Model, Provider
from celeste.constraints import Choice, ImageConstraint, ImagesConstraint
from celeste.mime_types import ImageMimeType
from celeste_video_generation.parameters import VideoGenerationParameter

# Supported MIME types for all Veo models
VEO_SUPPORTED_MIME_TYPES = [
    ImageMimeType.JPEG,
    ImageMimeType.PNG,
    ImageMimeType.WEBP,
]

MODELS: list[Model] = [
    Model(
        id="veo-3.0-generate-001",
        provider=Provider.GOOGLE,
        display_name="Veo 3",
        parameter_constraints={
            VideoGenerationParameter.ASPECT_RATIO: Choice(options=["16:9", "9:16"]),
            VideoGenerationParameter.RESOLUTION: Choice(options=["720p"]),
            VideoGenerationParameter.DURATION: Choice(options=[4, 6, 8]),
            VideoGenerationParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=VEO_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
    Model(
        id="veo-3.0-fast-generate-001",
        provider=Provider.GOOGLE,
        display_name="Veo 3 Fast",
        parameter_constraints={
            VideoGenerationParameter.ASPECT_RATIO: Choice(options=["16:9", "9:16"]),
            VideoGenerationParameter.RESOLUTION: Choice(options=["720p"]),
            VideoGenerationParameter.DURATION: Choice(options=[4, 6, 8]),
            VideoGenerationParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=VEO_SUPPORTED_MIME_TYPES
            ),
        },
    ),
    Model(
        id="veo-3.1-generate-preview",
        provider=Provider.GOOGLE,
        display_name="Veo 3.1 (Preview)",
        parameter_constraints={
            VideoGenerationParameter.ASPECT_RATIO: Choice(options=["16:9", "9:16"]),
            VideoGenerationParameter.RESOLUTION: Choice(options=["720p", "1080p"]),
            VideoGenerationParameter.DURATION: Choice(options=[4, 6, 8]),
            VideoGenerationParameter.REFERENCE_IMAGES: ImagesConstraint(
                supported_mime_types=VEO_SUPPORTED_MIME_TYPES,
                max_count=3,
            ),
            VideoGenerationParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=VEO_SUPPORTED_MIME_TYPES,
            ),
            VideoGenerationParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=VEO_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
    Model(
        id="veo-3.1-fast-generate-preview",
        provider=Provider.GOOGLE,
        display_name="Veo 3.1 Fast (Preview)",
        parameter_constraints={
            VideoGenerationParameter.ASPECT_RATIO: Choice(options=["16:9", "9:16"]),
            VideoGenerationParameter.RESOLUTION: Choice(options=["720p", "1080p"]),
            VideoGenerationParameter.DURATION: Choice(options=[4, 6, 8]),
            VideoGenerationParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=VEO_SUPPORTED_MIME_TYPES,
            ),
            VideoGenerationParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=VEO_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
]
