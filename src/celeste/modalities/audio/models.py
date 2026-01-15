"""Aggregated models for audio modality."""

from celeste.models import Model

from .providers.elevenlabs.models import MODELS as ELEVENLABS_MODELS
from .providers.google.models import MODELS as GOOGLE_MODELS
from .providers.gradium.models import MODELS as GRADIUM_MODELS
from .providers.openai.models import MODELS as OPENAI_MODELS

MODELS: list[Model] = [
    *ELEVENLABS_MODELS,
    *GOOGLE_MODELS,
    *GRADIUM_MODELS,
    *OPENAI_MODELS,
]
