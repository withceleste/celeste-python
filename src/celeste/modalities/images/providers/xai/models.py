"""xAI models for images modality."""

from celeste.constraints import Choice, Range
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import ImageParameter

MODELS: list[Model] = [
    Model(
        id="grok-imagine-image",
        provider=Provider.XAI,
        display_name="Grok Imagine Image",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.NUM_IMAGES: Range(min=1, max=10),
            ImageParameter.ASPECT_RATIO: Choice(
                options=[
                    "1:1",
                    "3:4",
                    "4:3",
                    "9:16",
                    "16:9",
                    "2:3",
                    "3:2",
                    "9:19.5",
                    "19.5:9",
                    "9:20",
                    "20:9",
                    "1:2",
                    "2:1",
                    "auto",
                ]
            ),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["url", "b64_json"]),
        },
    ),
]
