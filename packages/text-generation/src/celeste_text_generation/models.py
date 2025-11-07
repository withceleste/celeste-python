"""Model definitions for text generation."""

from celeste import Model
from celeste_text_generation.providers.anthropic.models import (
    MODELS as ANTHROPIC_MODELS,
)
from celeste_text_generation.providers.cohere.models import MODELS as COHERE_MODELS
from celeste_text_generation.providers.google.models import MODELS as GOOGLE_MODELS
from celeste_text_generation.providers.mistral.models import MODELS as MISTRAL_MODELS
from celeste_text_generation.providers.openai.models import MODELS as OPENAI_MODELS

MODELS: list[Model] = [
    *ANTHROPIC_MODELS,
    *COHERE_MODELS,
    *GOOGLE_MODELS,
    *MISTRAL_MODELS,
    *OPENAI_MODELS,
]
