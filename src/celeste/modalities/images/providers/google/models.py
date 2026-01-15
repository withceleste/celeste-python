"""Google models for images modality."""

from celeste.constraints import Choice, ImagesConstraint, Range
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import ImageParameter

# Imagen API models (instances[].prompt → predictions[])
IMAGEN_MODELS: list[Model] = [
    # Imagen 4 models (text-to-image) - Current GA
    Model(
        id="imagen-4.0-generate-001",
        provider=Provider.GOOGLE,
        display_name="Imagen 4",
        operations={Modality.IMAGES: {Operation.GENERATE}},
        parameter_constraints={
            ImageParameter.NUM_IMAGES: Range(min=1, max=4),
            ImageParameter.ASPECT_RATIO: Choice(
                options=["1:1", "3:4", "4:3", "9:16", "16:9"]
            ),
            ImageParameter.QUALITY: Choice(options=["1K", "2K"]),
        },
    ),
    Model(
        id="imagen-4.0-fast-generate-001",
        provider=Provider.GOOGLE,
        display_name="Imagen 4 Fast",
        operations={Modality.IMAGES: {Operation.GENERATE}},
        parameter_constraints={
            ImageParameter.NUM_IMAGES: Range(min=1, max=4),
            ImageParameter.ASPECT_RATIO: Choice(
                options=["1:1", "3:4", "4:3", "9:16", "16:9"]
            ),
            ImageParameter.QUALITY: Choice(options=["1K"]),
        },
    ),
    Model(
        id="imagen-4.0-ultra-generate-001",
        provider=Provider.GOOGLE,
        display_name="Imagen 4 Ultra",
        operations={Modality.IMAGES: {Operation.GENERATE}},
        parameter_constraints={
            ImageParameter.NUM_IMAGES: Range(min=1, max=4),
            ImageParameter.ASPECT_RATIO: Choice(
                options=["1:1", "3:4", "4:3", "9:16", "16:9"]
            ),
            ImageParameter.QUALITY: Choice(options=["1K", "2K"]),
        },
    ),
]

# Gemini API models (contents[].parts[] → candidates[])
GEMINI_MODELS: list[Model] = [
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
            ImageParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=3),
        },
    ),
    Model(
        id="gemini-3-pro-image-preview",
        provider=Provider.GOOGLE,
        display_name="Gemini 3 Pro Image (Preview)",
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
        },
    ),
]

# Unified model list for registration
MODELS: list[Model] = [
    *IMAGEN_MODELS,
    *GEMINI_MODELS,
]

__all__ = [
    "GEMINI_MODELS",
    "IMAGEN_MODELS",
    "MODELS",
]
