"""Google models for images modality."""

from celeste.constraints import Choice, ImagesConstraint
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import ImageParameter

GOOGLE_IMAGEN_MODELS: list[Model] = []

# Gemini API models (contents[].parts[] → candidates[])
GOOGLE_GEMINI_MODELS: list[Model] = [
    Model(
        id="gemini-2.5-flash-image",
        provider=Provider.GOOGLE,
        display_name="Gemini 2.5 Flash Image",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Choice(
                options=[
                    "1:1",
                    "2:3",
                    "3:2",
                    "3:4",
                    "4:3",
                    "4:5",
                    "5:4",
                    "9:16",
                    "16:9",
                    "21:9",
                ]
            ),
        },
    ),
    Model(
        id="gemini-3-pro-image",
        provider=Provider.GOOGLE,
        display_name="Nano Banana Pro",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Choice(
                options=[
                    "1:1",
                    "2:3",
                    "3:2",
                    "3:4",
                    "4:3",
                    "4:5",
                    "5:4",
                    "9:16",
                    "16:9",
                    "21:9",
                ]
            ),
            ImageParameter.QUALITY: Choice(options=["1K", "2K", "4K"]),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=14),
            ImageParameter.THINKING_LEVEL: Choice(options=["minimal", "high"]),
        },
    ),
    Model(
        id="gemini-3.1-flash-image",
        provider=Provider.GOOGLE,
        display_name="Nano Banana 2",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Choice(
                options=[
                    "1:1",
                    "1:4",
                    "1:8",
                    "2:3",
                    "3:2",
                    "3:4",
                    "4:1",
                    "4:3",
                    "4:5",
                    "5:4",
                    "8:1",
                    "9:16",
                    "16:9",
                    "21:9",
                ]
            ),
            ImageParameter.QUALITY: Choice(options=["512", "1K", "2K", "4K"]),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=14),
            ImageParameter.THINKING_LEVEL: Choice(options=["minimal", "high"]),
        },
    ),
    Model(
        id="gemini-3.1-flash-lite-image",
        provider=Provider.GOOGLE,
        display_name="Nano Banana 2 Lite",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Choice(
                options=[
                    "1:1",
                    "2:3",
                    "3:2",
                    "3:4",
                    "4:3",
                    "4:5",
                    "5:4",
                    "9:16",
                    "16:9",
                    "21:9",
                ]
            ),
            ImageParameter.QUALITY: Choice(options=["1K"]),
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=14),
            ImageParameter.THINKING_LEVEL: Choice(options=["minimal", "high"]),
        },
    ),
]

# Unified model list for registration
MODELS: list[Model] = [
    *GOOGLE_IMAGEN_MODELS,
    *GOOGLE_GEMINI_MODELS,
]

__all__ = [
    "GOOGLE_GEMINI_MODELS",
    "GOOGLE_IMAGEN_MODELS",
    "MODELS",
]
