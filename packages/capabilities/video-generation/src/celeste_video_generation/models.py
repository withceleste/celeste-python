"""Model definitions for video generation."""

from celeste import Model
from celeste_video_generation.providers.bytedance.models import (
    MODELS as BYTEDANCE_MODELS,
)
from celeste_video_generation.providers.google.models import MODELS as GOOGLE_MODELS
from celeste_video_generation.providers.openai.models import MODELS as OPENAI_MODELS

MODELS: list[Model] = [
    *BYTEDANCE_MODELS,
    *GOOGLE_MODELS,
    *OPENAI_MODELS,
]
