"""ElevenLabs audio client (dispatches TTS and STT wire backends)."""

from typing import Any, ClassVar

from celeste.providers.elevenlabs.text_to_speech.config import BASE_URL

from ...client import AudioClient
from .models import ELEVENLABS_STT_MODELS, ELEVENLABS_TTS_MODELS
from .speech_to_text import ElevenLabsSpeechToTextAudioClient
from .text_to_speech import ElevenLabsTextToSpeechAudioClient

_TTS_MODEL_IDS = frozenset(m.id for m in ELEVENLABS_TTS_MODELS)
_STT_MODEL_IDS = frozenset(m.id for m in ELEVENLABS_STT_MODELS)


class ElevenLabsAudioClient(AudioClient):
    """ElevenLabs audio client: constructing it returns the TTS or STT backend by model id."""

    _default_base_url: ClassVar[str] = BASE_URL

    def __new__(cls, **data: Any) -> Any:
        model_id = data["model"].id
        if model_id in _TTS_MODEL_IDS:
            return ElevenLabsTextToSpeechAudioClient(**data)
        if model_id in _STT_MODEL_IDS:
            return ElevenLabsSpeechToTextAudioClient(**data)
        msg = f"Unknown ElevenLabs audio model: {model_id}"
        raise ValueError(msg)


__all__ = ["ElevenLabsAudioClient"]
