"""OpenAI models for videos modality."""

from celeste.constraints import Choice, ImageConstraint
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import ImageMimeType
from celeste.models import Model

from ...parameters import VideoParameter

MODELS: list[Model] = [
    Model(
        id="sora-2",
        provider=Provider.OPENAI,
        display_name="Sora 2",
        operations={Modality.VIDEOS: {Operation.GENERATE}},
        parameter_constraints={
            VideoParameter.DURATION: Choice(options=["4", "8", "12"]),
            VideoParameter.ASPECT_RATIO: Choice(options=["16:9", "9:16"]),
            VideoParameter.RESOLUTION: Choice(options=["720p"]),
        },
    ),
    Model(
        id="sora-2-pro",
        provider=Provider.OPENAI,
        display_name="Sora 2 Pro",
        operations={Modality.VIDEOS: {Operation.GENERATE}},
        parameter_constraints={
            VideoParameter.DURATION: Choice(options=["4", "8", "12"]),
            VideoParameter.ASPECT_RATIO: Choice(options=["16:9", "9:16"]),
            VideoParameter.RESOLUTION: Choice(options=["720p"]),
            VideoParameter.FIRST_FRAME: ImageConstraint(
                supported_mime_types=[
                    ImageMimeType.JPEG,
                    ImageMimeType.PNG,
                    ImageMimeType.WEBP,
                ],
            ),
        },
    ),
    Model(
        id="sora-2-2025-12-08",
        provider=Provider.OPENAI,
        display_name="Sora 2 (December 2025)",
        operations={Modality.VIDEOS: {Operation.GENERATE}},
        parameter_constraints={
            VideoParameter.DURATION: Choice(options=["4", "8", "12"]),
            VideoParameter.ASPECT_RATIO: Choice(options=["16:9", "9:16"]),
            VideoParameter.RESOLUTION: Choice(options=["720p"]),
        },
    ),
]
