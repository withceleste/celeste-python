"""OpenAI models for images modality."""

from celeste.constraints import Choice, Range
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import ImageParameter

MODELS: list[Model] = [
    Model(
        id="dall-e-2",
        provider=Provider.OPENAI,
        display_name="DALL-E 2",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Choice(
                options=["256x256", "512x512", "1024x1024"]
            ),
        },
    ),
    Model(
        id="dall-e-3",
        provider=Provider.OPENAI,
        display_name="DALL-E 3",
        operations={Modality.IMAGES: {Operation.GENERATE}},
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Choice(
                options=["1024x1024", "1792x1024", "1024x1792"]
            ),
            ImageParameter.QUALITY: Choice(options=["standard", "hd"]),
        },
    ),
    Model(
        id="gpt-image-1",
        provider=Provider.OPENAI,
        display_name="GPT Image 1",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageParameter.ASPECT_RATIO: Choice(
                options=["1024x1024", "1536x1024", "1024x1536", "auto"]
            ),
            ImageParameter.QUALITY: Choice(options=["low", "medium", "high", "auto"]),
        },
    ),
    Model(
        id="gpt-image-1-mini",
        provider=Provider.OPENAI,
        display_name="GPT Image 1 Mini",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageParameter.ASPECT_RATIO: Choice(
                options=["1024x1024", "1024x1536", "1536x1024", "auto"]
            ),
            ImageParameter.QUALITY: Choice(options=["low", "medium", "high", "auto"]),
        },
    ),
    Model(
        id="gpt-image-1.5",
        provider=Provider.OPENAI,
        display_name="GPT Image 1.5",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=False,
        parameter_constraints={
            ImageParameter.ASPECT_RATIO: Choice(
                options=["1024x1024", "1536x1024", "1024x1536", "auto"]
            ),
            ImageParameter.QUALITY: Choice(options=["low", "medium", "high", "auto"]),
        },
    ),
]
