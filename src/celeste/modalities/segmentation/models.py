"""Aggregated models for segmentation modality."""

from celeste.models import Model

from .providers.fal.models import MODELS as FAL_MODELS

MODELS: list[Model] = [
    *FAL_MODELS,
]
