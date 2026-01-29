"""Aggregated models for videos modality."""

from celeste.models import Model

from .providers.byteplus.models import MODELS as BYTEPLUS_MODELS
from .providers.google.models import MODELS as GOOGLE_MODELS
from .providers.openai.models import MODELS as OPENAI_MODELS
from .providers.xai.models import MODELS as XAI_MODELS

MODELS: list[Model] = [
    *BYTEPLUS_MODELS,
    *GOOGLE_MODELS,
    *OPENAI_MODELS,
    *XAI_MODELS,
]
