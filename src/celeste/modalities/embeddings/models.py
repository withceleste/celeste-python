"""Aggregated models for embeddings modality."""

from celeste.models import Model

from .providers.google.models import MODELS as GOOGLE_MODELS

MODELS: list[Model] = [
    *GOOGLE_MODELS,
]
