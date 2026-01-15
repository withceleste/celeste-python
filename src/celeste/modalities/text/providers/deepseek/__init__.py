"""DeepSeek provider for text modality."""

from .client import DeepSeekTextClient
from .models import MODELS

__all__ = ["MODELS", "DeepSeekTextClient"]
