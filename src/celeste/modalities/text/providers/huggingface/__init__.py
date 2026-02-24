"""HuggingFace provider for text modality."""

from .client import HuggingFaceTextClient
from .models import MODELS

__all__ = ["MODELS", "HuggingFaceTextClient"]
