"""Google models for image generation."""

from celeste import Model, Provider
from celeste.constraints import Choice
from celeste_image_generation.parameters import ImageGenerationParameter

# Imagen API models (instances[].prompt → predictions[])
IMAGEN_MODELS: list[Model] = [
    # Imagen 4 models (text-to-image) - Current GA
    Model(
        id="imagen-4.0-generate-001",
        provider=Provider.GOOGLE,
        display_name="Imagen 4",
        parameter_constraints={
            ImageGenerationParameter.ASPECT_RATIO: Choice(
                options=["1:1", "3:4", "4:3", "9:16", "16:9"]
            ),
            ImageGenerationParameter.QUALITY: Choice(options=["1K", "2K"]),
        },
    ),
    Model(
        id="imagen-4.0-fast-generate-001",
        provider=Provider.GOOGLE,
        display_name="Imagen 4 Fast",
        parameter_constraints={
            ImageGenerationParameter.ASPECT_RATIO: Choice(
                options=["1:1", "3:4", "4:3", "9:16", "16:9"]
            ),
            ImageGenerationParameter.QUALITY: Choice(options=["1K"]),
        },
    ),
    Model(
        id="imagen-4.0-ultra-generate-001",
        provider=Provider.GOOGLE,
        display_name="Imagen 4 Ultra",
        parameter_constraints={
            ImageGenerationParameter.ASPECT_RATIO: Choice(
                options=["1:1", "3:4", "4:3", "9:16", "16:9"]
            ),
            ImageGenerationParameter.QUALITY: Choice(options=["1K", "2K"]),
        },
    ),
    # Imagen 3 models (deprecated June 24, 2025) - Support for backwards compatibility
    Model(
        id="imagen-3.0-generate-002",
        provider=Provider.GOOGLE,
        display_name="Imagen 3",
        parameter_constraints={
            ImageGenerationParameter.ASPECT_RATIO: Choice(
                options=["1:1", "3:4", "4:3", "9:16", "16:9"]
            ),
            ImageGenerationParameter.QUALITY: Choice(options=["1K"]),
        },
    ),
]

# Gemini API models (contents[].parts[] → candidates[])
GEMINI_MODELS: list[Model] = [
    Model(
        id="gemini-2.5-flash-image",
        provider=Provider.GOOGLE,
        display_name="Gemini 2.5 Flash Image",
        parameter_constraints={
            ImageGenerationParameter.ASPECT_RATIO: Choice(
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
]

# Unified model list for registration
MODELS: list[Model] = [
    *IMAGEN_MODELS,
    *GEMINI_MODELS,
]
