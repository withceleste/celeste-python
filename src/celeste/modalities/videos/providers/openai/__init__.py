"""OpenAI provider for videos modality."""

from .client import OpenAIVideosClient
from .models import MODELS

__all__ = ["MODELS", "OpenAIVideosClient"]
