"""Aggregated models for images modality."""

from celeste.models import Model

from .providers.bfl.models import MODELS as BFL_MODELS
from .providers.byteplus.models import MODELS as BYTEPLUS_MODELS
from .providers.google.models import MODELS as GOOGLE_MODELS
from .providers.openai.models import MODELS as OPENAI_MODELS
from .providers.xai.models import MODELS as XAI_MODELS

MODELS: list[Model] = [
    *BFL_MODELS,
    *BYTEPLUS_MODELS,
    *GOOGLE_MODELS,
    *OPENAI_MODELS,
    *XAI_MODELS,
]
