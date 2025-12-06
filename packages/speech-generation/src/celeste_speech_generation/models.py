"""Model definitions for speech generation."""

from celeste import Model
from celeste_speech_generation.providers.elevenlabs.models import (
    MODELS as ELEVENLABS_MODELS,
)
from celeste_speech_generation.providers.google.models import MODELS as GOOGLE_MODELS
from celeste_speech_generation.providers.gradium.models import MODELS as GRADIUM_MODELS
from celeste_speech_generation.providers.openai.models import MODELS as OPENAI_MODELS

MODELS: list[Model] = [
    *GOOGLE_MODELS,
    *OPENAI_MODELS,
    *ELEVENLABS_MODELS,
    *GRADIUM_MODELS,
]
