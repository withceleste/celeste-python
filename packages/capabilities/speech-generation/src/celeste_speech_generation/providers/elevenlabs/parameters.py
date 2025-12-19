"""ElevenLabs Text To Speech parameter mappers for speech generation."""

from celeste_elevenlabs.text_to_speech.parameters import (
    LanguageCodeMapper as _LanguageCodeMapper,
)
from celeste_elevenlabs.text_to_speech.parameters import (
    OutputFormatMapper as _OutputFormatMapper,
)
from celeste_elevenlabs.text_to_speech.parameters import (
    SpeedMapper as _SpeedMapper,
)
from celeste_elevenlabs.text_to_speech.parameters import (
    VoiceMapper as _VoiceMapper,
)

from celeste.parameters import ParameterMapper
from celeste_speech_generation.parameters import SpeechGenerationParameter


class VoiceMapper(_VoiceMapper):
    name = SpeechGenerationParameter.VOICE


class OutputFormatMapper(_OutputFormatMapper):
    name = SpeechGenerationParameter.OUTPUT_FORMAT


class SpeedMapper(_SpeedMapper):
    name = SpeechGenerationParameter.SPEED


class LanguageCodeMapper(_LanguageCodeMapper):
    name = SpeechGenerationParameter.LANGUAGE


ELEVENLABS_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
    OutputFormatMapper(),
    SpeedMapper(),
    LanguageCodeMapper(),
]

__all__ = ["ELEVENLABS_PARAMETER_MAPPERS"]
