"""BytePlus models for videos modality.

Model IDs use lowercase format with version suffixes (e.g., seedance-1-0-pro-250528).
Console display names differ from API model IDs.
"""

from celeste.constraints import Choice, ImageConstraint, ImagesConstraint, Range
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import ImageMimeType
from celeste.models import Model

from ...parameters import VideoParameter

# Supported MIME types for BytePlus image parameters
BYTEPLUS_SUPPORTED_MIME_TYPES = [
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
        provider=Provider.BYTEPLUS,
        operations={Modality.VIDEOS: {Operation.GENERATE}},
        display_name="Seedance 1.0 Lite (Text-to-Video)",
        parameter_constraints={
            VideoParameter.DURATION: Range(min=2, max=12),
            VideoParameter.RESOLUTION: Choice(options=["480p", "720p", "1080p"]),
            VideoParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=BYTEPLUS_SUPPORTED_MIME_TYPES,
            ),
            VideoParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=BYTEPLUS_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
    Model(
        id="seedance-1-0-lite-i2v-250428",
        provider=Provider.BYTEPLUS,
        operations={Modality.VIDEOS: {Operation.GENERATE}},
        display_name="Seedance 1.0 Lite (Image-to-Video)",
        parameter_constraints={
            VideoParameter.DURATION: Range(min=2, max=12),
            VideoParameter.RESOLUTION: Choice(options=["480p", "720p", "1080p"]),
            VideoParameter.REFERENCE_IMAGES: ImagesConstraint(
                supported_mime_types=BYTEPLUS_SUPPORTED_MIME_TYPES,
                max_count=4,
            ),
            VideoParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=BYTEPLUS_SUPPORTED_MIME_TYPES,
            ),
            VideoParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=BYTEPLUS_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
    Model(
        id="seedance-1-0-pro-250528",
        provider=Provider.BYTEPLUS,
        operations={Modality.VIDEOS: {Operation.GENERATE}},
        display_name="Seedance 1.0 Pro",
        parameter_constraints={
            VideoParameter.DURATION: Range(min=2, max=12),
            VideoParameter.RESOLUTION: Choice(options=["480p", "720p", "1080p"]),
            VideoParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=BYTEPLUS_SUPPORTED_MIME_TYPES,
            ),
            VideoParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=BYTEPLUS_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
    Model(
        id="seedance-1-0-pro-fast-251015",
        provider=Provider.BYTEPLUS,
        operations={Modality.VIDEOS: {Operation.GENERATE}},
        display_name="Seedance 1.0 Pro Fast",
        parameter_constraints={
            VideoParameter.DURATION: Range(min=2, max=12),
            VideoParameter.RESOLUTION: Choice(options=["480p", "720p", "1080p"]),
            VideoParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=BYTEPLUS_SUPPORTED_MIME_TYPES,
            ),
            VideoParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=BYTEPLUS_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
    Model(
        id="seedance-1-5-pro-251215",
        provider=Provider.BYTEPLUS,
        operations={Modality.VIDEOS: {Operation.GENERATE}},
        display_name="Seedance 1.5 Pro",
        parameter_constraints={
            VideoParameter.DURATION: Range(min=4, max=12),
            VideoParameter.RESOLUTION: Choice(options=["480p", "720p"]),
            VideoParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=BYTEPLUS_SUPPORTED_MIME_TYPES,
            ),
            VideoParameter.LAST_FRAME: ImageConstraint(
                supported_mime_types=BYTEPLUS_SUPPORTED_MIME_TYPES,
            ),
        },
    ),
]
