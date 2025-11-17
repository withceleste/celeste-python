"""OpenAI models for image generation."""

from celeste import Model, Provider
from celeste.constraints import Choice, Range
from celeste_image_generation.parameters import ImageGenerationParameter

MODELS: list[Model] = [
    Model(
        id="dall-e-2",
        provider=Provider.OPENAI,
        display_name="DALL-E 2",
        parameter_constraints={
            ImageGenerationParameter.ASPECT_RATIO: Choice(
                options=["256x256", "512x512", "1024x1024"]
            ),
        },
    ),
    Model(
        id="dall-e-3",
        provider=Provider.OPENAI,
        display_name="DALL-E 3",
        parameter_constraints={
            ImageGenerationParameter.ASPECT_RATIO: Choice(
                options=["1024x1024", "1792x1024", "1024x1792"]
            ),
            ImageGenerationParameter.QUALITY: Choice(options=["standard", "hd"]),
        },
    ),
    Model(
        id="gpt-image-1",
        provider=Provider.OPENAI,
        display_name="GPT Image 1",
        streaming=True,
        parameter_constraints={
            ImageGenerationParameter.PARTIAL_IMAGES: Range(min=0, max=3),
            ImageGenerationParameter.ASPECT_RATIO: Choice(
                options=["1024x1024", "1536x1024", "1024x1536", "auto"]
            ),
            ImageGenerationParameter.QUALITY: Choice(
                options=["low", "medium", "high", "auto"]
            ),
        },
    ),
]
