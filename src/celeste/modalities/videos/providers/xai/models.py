"""xAI models for videos modality."""

from celeste.constraints import Choice, ImageConstraint, Range
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import VideoParameter

MODELS: list[Model] = [
    Model(
        id="grok-imagine-video",
        provider=Provider.XAI,
        display_name="Grok Imagine Video",
        operations={Modality.VIDEOS: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            VideoParameter.DURATION: Range(min=1, max=15),
            VideoParameter.ASPECT_RATIO: Choice(
                options=["16:9", "4:3", "1:1", "9:16", "3:4", "3:2", "2:3"]
            ),
            VideoParameter.RESOLUTION: Choice(options=["720p", "480p"]),
            VideoParameter.FIRST_FRAME: ImageConstraint(),
        },
    ),
    Model(
        id="grok-imagine-video-1.5",
        provider=Provider.XAI,
        display_name="Grok Imagine Video 1.5",
        operations={Modality.VIDEOS: {Operation.GENERATE}},
        parameter_constraints={
            VideoParameter.DURATION: Range(min=1, max=15),
            VideoParameter.ASPECT_RATIO: Choice(
                options=["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"]
            ),
            VideoParameter.RESOLUTION: Choice(options=["480p", "720p", "1080p"]),
            VideoParameter.FIRST_FRAME: ImageConstraint(),
        },
    ),
]
