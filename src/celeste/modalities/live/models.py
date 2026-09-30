"""Aggregated models for live modality."""

from celeste.models import Model

from .providers.google.models import MODELS as GOOGLE_MODELS
from .providers.openai.models import MODELS as OPENAI_MODELS

MODELS: list[Model] = [*GOOGLE_MODELS, *OPENAI_MODELS]
