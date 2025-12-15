"""Model definitions for video generation."""

from celeste import Model
from celeste_video_generation.providers.byteplus.models import (
    MODELS as BYTEPLUS_MODELS,
)
from celeste_video_generation.providers.google.models import MODELS as GOOGLE_MODELS
from celeste_video_generation.providers.openai.models import MODELS as OPENAI_MODELS

MODELS: list[Model] = [
    *BYTEPLUS_MODELS,
    *GOOGLE_MODELS,
    *OPENAI_MODELS,
]
