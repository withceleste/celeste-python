"""BFL (Black Forest Labs) models for videos modality."""

from celeste.constraints import Choice, ImageConstraint, Range
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import VideoParameter

MODELS: list[Model] = [
    Model(
        id="flux-3-video",
        provider=Provider.BFL,
        display_name="FLUX 3 Video",
        operations={Modality.VIDEOS: {Operation.GENERATE}},
        parameter_constraints={
            VideoParameter.DURATION: Range(min=5, max=20),
            VideoParameter.ASPECT_RATIO: Choice(
                options=[
                    "21:9",
                    "2:1",
                    "16:9",
                    "4:3",
                    "1:1",
                    "3:4",
                    "9:16",
                    "9:21",
                    "auto",
                ]
            ),
            VideoParameter.RESOLUTION: Choice(options=["hd", "fhd", "qhd", "uhd"]),
            VideoParameter.FIRST_FRAME: ImageConstraint(),
            VideoParameter.LAST_FRAME: ImageConstraint(),
        },
    ),
]
