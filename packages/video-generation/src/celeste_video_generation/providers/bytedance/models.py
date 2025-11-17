"""ByteDance models for video generation.

Model IDs use lowercase format with version suffixes (e.g., seedance-1-0-pro-250528).
Console display names differ from API model IDs.
"""

from celeste import Capability, Model, Provider
from celeste.constraints import Choice, ImageConstraint, ImagesConstraint, Range
from celeste.mime_types import ImageMimeType
from celeste_video_generation.parameters import VideoGenerationParameter

# Supported MIME types for ByteDance image parameters
BYTEDANCE_SUPPORTED_MIME_TYPES = [
    ImageMimeType.JPEG,
    ImageMimeType.PNG,
    ImageMimeType.WEBP,
    ImageMimeType.BMP,
    ImageMimeType.TIFF,
    ImageMimeType.GIF,
]

MODELS: list[Model] = [
    Model(
        id="seedance-1-0-lite-t2v-250428",
        provider=Provider.BYTEDANCE,
        capabilities={Capability.VIDEO_GENERATION},
        display_name="Seedance 1.0 Lite (Text-to-Video)",
        parameter_constraints={
            VideoGenerationParameter.DURATION: Range(min=2, max=12),
            VideoGenerationParameter.RESOLUTION: Choice(
                options=["480p", "720p", "1080p"]
            ),
            VideoGenerationParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=BYTEDANCE_SUPPORTED_MIME_TYPES,
            ),
            VideoGenerationParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=BYTEDANCE_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
    Model(
        id="seedance-1-0-lite-i2v-250428",
        provider=Provider.BYTEDANCE,
        capabilities={Capability.VIDEO_GENERATION},
        display_name="Seedance 1.0 Lite (Image-to-Video)",
        parameter_constraints={
            VideoGenerationParameter.DURATION: Range(min=2, max=12),
            VideoGenerationParameter.RESOLUTION: Choice(
                options=["480p", "720p", "1080p"]
            ),
            VideoGenerationParameter.REFERENCE_IMAGES: ImagesConstraint(
                supported_mime_types=BYTEDANCE_SUPPORTED_MIME_TYPES,
                max_count=4,
            ),
            VideoGenerationParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=BYTEDANCE_SUPPORTED_MIME_TYPES,
            ),
            VideoGenerationParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=BYTEDANCE_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
    Model(
        id="seedance-1-0-pro-250528",
        provider=Provider.BYTEDANCE,
        capabilities={Capability.VIDEO_GENERATION},
        display_name="Seedance 1.0 Pro",
        parameter_constraints={
            VideoGenerationParameter.DURATION: Range(min=2, max=12),
            VideoGenerationParameter.RESOLUTION: Choice(
                options=["480p", "720p", "1080p"]
            ),
            VideoGenerationParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=BYTEDANCE_SUPPORTED_MIME_TYPES,
            ),
            VideoGenerationParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=BYTEDANCE_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
    Model(
        id="seedance-1-0-pro-fast-251015",
        provider=Provider.BYTEDANCE,
        capabilities={Capability.VIDEO_GENERATION},
        display_name="Seedance 1.0 Pro Fast",
        parameter_constraints={
            VideoGenerationParameter.DURATION: Range(min=2, max=12),
            VideoGenerationParameter.RESOLUTION: Choice(
                options=["480p", "720p", "1080p"]
            ),
            VideoGenerationParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=BYTEDANCE_SUPPORTED_MIME_TYPES,
            ),
            VideoGenerationParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=BYTEDANCE_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
]
