"""BFL models for the videos modality."""

from celeste.constraints import (
    Bool,
    Choice,
    ImageConstraint,
    Range,
    VideoConstraint,
)
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...constraints import VideoKeyframesConstraint
from ...parameters import VideoParameter

MODELS: list[Model] = [
    Model(
        id="flux-3-video",
        provider=Provider.BFL,
        display_name="FLUX 3 Video",
        operations={Modality.VIDEOS: {Operation.GENERATE, Operation.ENHANCE}},
        parameter_constraints={
            VideoParameter.ASPECT_RATIO: Choice(
                options=["auto", "21:9", "2:1", "16:9", "4:3", "1:1", "3:4", "9:16"]
            ),
            VideoParameter.RESOLUTION: Choice(options=["720p", "1080p"]),
            VideoParameter.DURATION: Choice(options=["auto", *range(5, 21)]),
            VideoParameter.FIRST_FRAME: ImageConstraint(),
            VideoParameter.LAST_FRAME: ImageConstraint(),
            VideoParameter.KEYFRAMES: VideoKeyframesConstraint(
                max_count=10,
                max_timestamp=20,
            ),
            VideoParameter.START_VIDEO: VideoConstraint(),
            VideoParameter.GENERATE_AUDIO: Bool(),
            VideoParameter.SAFETY_TOLERANCE: Range(min=0, max=4, step=1),
            VideoParameter.DRAFT: Bool(),
        },
        streaming=False,
    )
]

__all__ = ["MODELS"]
