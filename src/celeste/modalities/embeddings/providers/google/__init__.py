"""Google provider for embeddings modality."""

from .client import GoogleEmbeddingsClient
from .models import MODELS

__all__ = ["MODELS", "GoogleEmbeddingsClient"]
