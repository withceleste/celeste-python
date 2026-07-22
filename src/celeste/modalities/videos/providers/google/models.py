"""Google models for videos modality."""

from celeste.constraints import Choice, ImageConstraint, ImagesConstraint, Range
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import ImageMimeType
from celeste.models import Model

from ...parameters import VideoParameter

# Supported MIME types for all Veo models
GOOGLE_SUPPORTED_MIME_TYPES = [
    ImageMimeType.JPEG,
    ImageMimeType.PNG,
    ImageMimeType.WEBP,
]

# Veo API models (predictLongRunning)
GOOGLE_VEO_MODELS: list[Model] = [
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
                supported_mime_types=GOOGLE_SUPPORTED_MIME_TYPES,
                max_count=3,
            ),
            VideoParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=GOOGLE_SUPPORTED_MIME_TYPES,
            ),
            VideoParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=GOOGLE_SUPPORTED_MIME_TYPES,
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
                supported_mime_types=GOOGLE_SUPPORTED_MIME_TYPES,
            ),
            VideoParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=GOOGLE_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
    Model(
        id="veo-3.1-lite-generate-preview",
        provider=Provider.GOOGLE,
        display_name="Veo 3.1 Lite (Preview)",
        operations={Modality.VIDEOS: {Operation.GENERATE}},
        parameter_constraints={
            VideoParameter.ASPECT_RATIO: Choice(options=["16:9", "9:16"]),
            VideoParameter.RESOLUTION: Choice(options=["720p", "1080p"]),
            VideoParameter.DURATION: Choice(options=[4, 6, 8]),
            VideoParameter.REFERENCE_IMAGES: ImagesConstraint(
                supported_mime_types=GOOGLE_SUPPORTED_MIME_TYPES,
                max_count=3,
            ),
            VideoParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=GOOGLE_SUPPORTED_MIME_TYPES,
            ),
            VideoParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=GOOGLE_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
]

# Interactions API models (Gemini Omni)
GOOGLE_OMNI_MODELS: list[Model] = [
    Model(
        id="gemini-omni-flash-preview",
        provider=Provider.GOOGLE,
        display_name="Gemini Omni Flash (Preview)",
        operations={Modality.VIDEOS: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            VideoParameter.ASPECT_RATIO: Choice(options=["16:9", "9:16"]),
            VideoParameter.DURATION: Range(min=3, max=10),
            VideoParameter.FIRST_FRAME: ImageConstraint(),
            VideoParameter.REFERENCE_IMAGES: ImagesConstraint(),
        },
    ),
]

MODELS: list[Model] = [
    *GOOGLE_VEO_MODELS,
    *GOOGLE_OMNI_MODELS,
]

__all__ = [
    "GOOGLE_OMNI_MODELS",
    "GOOGLE_VEO_MODELS",
    "MODELS",
]
