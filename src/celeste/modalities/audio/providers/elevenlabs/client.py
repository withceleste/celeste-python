"""ElevenLabs audio client (dispatches TTS and STT wire backends)."""

from typing import ClassVar

from celeste.client import Forward
from celeste.parameters import ParameterMapper
from celeste.providers.elevenlabs.text_to_speech.config import BASE_URL
from celeste.types import AudioContent

from ...client import AudioClient
from .models import ELEVENLABS_STT_MODELS, ELEVENLABS_TTS_MODELS
from .parameters import (
    ELEVENLABS_SPEECH_TO_TEXT_PARAMETER_MAPPERS,
    ELEVENLABS_TEXT_TO_SPEECH_PARAMETER_MAPPERS,
)
from .speech_to_text import ElevenLabsSpeechToTextAudioClient
from .text_to_speech import ElevenLabsTextToSpeechAudioClient

_TTS_MODEL_IDS = frozenset(m.id for m in ELEVENLABS_TTS_MODELS)
_STT_MODEL_IDS = frozenset(m.id for m in ELEVENLABS_STT_MODELS)


class ElevenLabsAudioClient(AudioClient):
    """ElevenLabs audio client (selects TTS or STT backend by model id)."""

    _default_base_url: ClassVar[str] = BASE_URL
    _strategy: (
        ElevenLabsTextToSpeechAudioClient | ElevenLabsSpeechToTextAudioClient | None
    ) = None

    def model_post_init(self, __context: object) -> None:
        """Select the backend once by model id."""
        super().model_post_init(__context)

        StrategyClass: type[AudioClient]
        if self.model.id in _TTS_MODEL_IDS:
            StrategyClass = ElevenLabsTextToSpeechAudioClient
        elif self.model.id in _STT_MODEL_IDS:
            StrategyClass = ElevenLabsSpeechToTextAudioClient
        else:
            msg = f"Unknown ElevenLabs audio model: {self.model.id}"
            raise ValueError(msg)

        strategy = StrategyClass(
            modality=self.modality,
            model=self.model,
            provider=self.provider,
            auth=self.auth,
            base_url=self.base_url,
        )
        object.__setattr__(self, "_strategy", strategy)

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[AudioContent]]:
        return [
            *ELEVENLABS_TEXT_TO_SPEECH_PARAMETER_MAPPERS,
            *ELEVENLABS_SPEECH_TO_TEXT_PARAMETER_MAPPERS,
        ]

    _speak_endpoint = Forward()
    _transcribe_endpoint = Forward()
    _init_request = Forward()
    _build_request = Forward()
    _make_request = Forward()
    _parse_content = Forward()
    _parse_usage = Forward()
    _parse_finish_reason = Forward()
    _transform_output = Forward()
    _build_metadata = Forward()
    _make_stream_request = Forward()
    _stream_class = Forward()


__all__ = ["ElevenLabsAudioClient"]
