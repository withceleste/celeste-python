"""Model definitions for image generation."""

from celeste import Model
from celeste_image_generation.providers.bfl.models import MODELS as BFL_MODELS
from celeste_image_generation.providers.byteplus.models import (
    MODELS as BYTEPLUS_MODELS,
)
from celeste_image_generation.providers.google.models import MODELS as GOOGLE_MODELS
from celeste_image_generation.providers.openai.models import MODELS as OPENAI_MODELS

MODELS: list[Model] = [
    *BFL_MODELS,
    *BYTEPLUS_MODELS,
    *GOOGLE_MODELS,
    *OPENAI_MODELS,
]
