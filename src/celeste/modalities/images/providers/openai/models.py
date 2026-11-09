"""OpenAI models for images modality."""

from celeste.constraints import Choice, Range, Str
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import ImageParameter

MODELS: list[Model] = [
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
            ImageParameter.NUM_IMAGES: Range(min=1, max=10),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["png", "jpeg", "webp"]),
            ImageParameter.BACKGROUND: Choice(
                options=["transparent", "opaque", "auto"]
            ),
            ImageParameter.SAFETY_TOLERANCE: Choice(options=["auto", "low"]),
            ImageParameter.OUTPUT_COMPRESSION: Range(min=0, max=100),
        },
    ),
    Model(
        id="gpt-image-1.5",
        provider=Provider.OPENAI,
        display_name="GPT Image 1.5",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageParameter.ASPECT_RATIO: Choice(
                options=["1024x1024", "1536x1024", "1024x1536", "auto"]
            ),
            ImageParameter.QUALITY: Choice(options=["low", "medium", "high", "auto"]),
            ImageParameter.NUM_IMAGES: Range(min=1, max=10),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["png", "jpeg", "webp"]),
            ImageParameter.BACKGROUND: Choice(
                options=["transparent", "opaque", "auto"]
            ),
            ImageParameter.SAFETY_TOLERANCE: Choice(options=["auto", "low"]),
            ImageParameter.OUTPUT_COMPRESSION: Range(min=0, max=100),
        },
    ),
    Model(
        id="gpt-image-2",
        provider=Provider.OPENAI,
        display_name="GPT Image 2",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageParameter.ASPECT_RATIO: Str(
                description="WIDTHxHEIGHT, such as 1536x864, with both edges divisible by 16, an aspect ratio between 1:3 and 3:1 and at most 3840x2160; or auto."
            ),
            ImageParameter.QUALITY: Choice(options=["low", "medium", "high", "auto"]),
            ImageParameter.NUM_IMAGES: Range(min=1, max=10),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["png", "jpeg", "webp"]),
            ImageParameter.BACKGROUND: Choice(
                options=["transparent", "opaque", "auto"]
            ),
            ImageParameter.SAFETY_TOLERANCE: Choice(options=["auto", "low"]),
            ImageParameter.OUTPUT_COMPRESSION: Range(min=0, max=100),
        },
    ),
    Model(
        id="gpt-image-2.5-flare",
        provider=Provider.OPENAI,
        display_name="GPT Image 2.5 Flare",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageParameter.ASPECT_RATIO: Str(
                description="WIDTHxHEIGHT, such as 1536x864, with both edges divisible by 16, an aspect ratio between 1:3 and 3:1 and at most 3840x2160; or auto."
            ),
            ImageParameter.QUALITY: Choice(
                options=["low", "medium", "high", "xhigh", "max", "auto"]
            ),
            ImageParameter.NUM_IMAGES: Range(min=1, max=10),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["png", "jpeg", "webp"]),
            ImageParameter.BACKGROUND: Choice(
                options=["transparent", "opaque", "auto"]
            ),
            ImageParameter.SAFETY_TOLERANCE: Choice(options=["auto", "low"]),
            ImageParameter.OUTPUT_COMPRESSION: Range(min=0, max=100),
        },
    ),
    Model(
        id="gpt-image-2.6-flare",
        provider=Provider.OPENAI,
        display_name="GPT Image 2.6 Flare",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageParameter.ASPECT_RATIO: Choice(
                options=["1024x1024", "1536x1024", "1024x1536", "auto"]
            ),
            ImageParameter.QUALITY: Choice(options=["low", "medium", "high", "auto"]),
            ImageParameter.NUM_IMAGES: Range(min=1, max=10),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["png", "jpeg", "webp"]),
            ImageParameter.BACKGROUND: Choice(
                options=["transparent", "opaque", "auto"]
            ),
            ImageParameter.SAFETY_TOLERANCE: Choice(options=["auto", "low"]),
            ImageParameter.OUTPUT_COMPRESSION: Range(min=0, max=100),
        },
    ),
    Model(
        id="gpt-image-2.5-sunburst",
        provider=Provider.OPENAI,
        display_name="GPT Image 2.5 Sunburst",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageParameter.ASPECT_RATIO: Str(
                description="WIDTHxHEIGHT, such as 1536x864, with both edges divisible by 16, an aspect ratio between 1:3 and 3:1 and at most 3840x2160; or auto."
            ),
            ImageParameter.QUALITY: Choice(
                options=["low", "medium", "high", "xhigh", "max", "auto"]
            ),
            ImageParameter.NUM_IMAGES: Range(min=1, max=10),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["png", "jpeg", "webp"]),
            ImageParameter.BACKGROUND: Choice(
                options=["transparent", "opaque", "auto"]
            ),
            ImageParameter.SAFETY_TOLERANCE: Choice(options=["auto", "low"]),
            ImageParameter.OUTPUT_COMPRESSION: Range(min=0, max=100),
        },
    ),
    Model(
        id="gpt-image-2.6-sunburst",
        provider=Provider.OPENAI,
        display_name="GPT Image 2.6 Sunburst",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
        streaming=True,
        parameter_constraints={
            ImageParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageParameter.ASPECT_RATIO: Choice(
                options=["1024x1024", "1536x1024", "1024x1536", "auto"]
            ),
            ImageParameter.QUALITY: Choice(options=["low", "medium", "high", "auto"]),
            ImageParameter.NUM_IMAGES: Range(min=1, max=10),
            ImageParameter.OUTPUT_FORMAT: Choice(options=["png", "jpeg", "webp"]),
            ImageParameter.BACKGROUND: Choice(
                options=["transparent", "opaque", "auto"]
            ),
            ImageParameter.SAFETY_TOLERANCE: Choice(options=["auto", "low"]),
            ImageParameter.OUTPUT_COMPRESSION: Range(min=0, max=100),
        },
    ),
]
