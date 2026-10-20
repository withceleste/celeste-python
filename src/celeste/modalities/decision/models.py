"""Aggregated models for decision modality."""

from celeste.models import Model

from .providers.typesafe.models import MODELS as TYPESAFE_MODELS

MODELS: list[Model] = [
    *TYPESAFE_MODELS,
]
