"""ElevenLabs provider for audio modality."""

from .client import ElevenLabsAudioClient
from .models import MODELS

__all__ = ["MODELS", "ElevenLabsAudioClient"]
