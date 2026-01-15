"""Google models for videos modality."""

from celeste.constraints import Choice, ImageConstraint, ImagesConstraint
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import ImageMimeType
from celeste.models import Model

from ...parameters import VideoParameter

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
        operations={Modality.VIDEOS: {Operation.GENERATE}},
        parameter_constraints={
            VideoParameter.ASPECT_RATIO: Choice(options=["16:9", "9:16"]),
            VideoParameter.RESOLUTION: Choice(options=["720p"]),
            VideoParameter.DURATION: Choice(options=[4, 6, 8]),
            VideoParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=VEO_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
    Model(
        id="veo-3.0-fast-generate-001",
        provider=Provider.GOOGLE,
        display_name="Veo 3 Fast",
        operations={Modality.VIDEOS: {Operation.GENERATE}},
        parameter_constraints={
            VideoParameter.ASPECT_RATIO: Choice(options=["16:9", "9:16"]),
            VideoParameter.RESOLUTION: Choice(options=["720p"]),
            VideoParameter.DURATION: Choice(options=[4, 6, 8]),
            VideoParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=VEO_SUPPORTED_MIME_TYPES
            ),
        },
    ),
    Model(
        id="veo-3.1-generate-preview",
        provider=Provider.GOOGLE,
        display_name="Veo 3.1 (Preview)",
        operations={Modality.VIDEOS: {Operation.GENERATE}},
        parameter_constraints={
            VideoParameter.ASPECT_RATIO: Choice(options=["16:9", "9:16"]),
            VideoParameter.RESOLUTION: Choice(options=["720p", "1080p", "4k"]),
            VideoParameter.DURATION: Choice(options=[4, 6, 8]),
            VideoParameter.REFERENCE_IMAGES: ImagesConstraint(
                supported_mime_types=VEO_SUPPORTED_MIME_TYPES,
                max_count=3,
            ),
            VideoParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=VEO_SUPPORTED_MIME_TYPES,
            ),
            VideoParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=VEO_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
    Model(
        id="veo-3.1-fast-generate-preview",
        provider=Provider.GOOGLE,
        display_name="Veo 3.1 Fast (Preview)",
        operations={Modality.VIDEOS: {Operation.GENERATE}},
        parameter_constraints={
            VideoParameter.ASPECT_RATIO: Choice(options=["16:9", "9:16"]),
            VideoParameter.RESOLUTION: Choice(options=["720p", "1080p", "4k"]),
            VideoParameter.DURATION: Choice(options=[4, 6, 8]),
            VideoParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=VEO_SUPPORTED_MIME_TYPES,
            ),
            VideoParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=VEO_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
]
