"""OpenAI Audio parameter mappers for speech generation."""

from celeste_openai.audio.parameters import (
    ResponseFormatMapper as _ResponseFormatMapper,
)
from celeste_openai.audio.parameters import (
    SpeedMapper as _SpeedMapper,
)
from celeste_openai.audio.parameters import (
    VoiceMapper as _VoiceMapper,
)

from celeste.parameters import ParameterMapper
from celeste_speech_generation.parameters import SpeechGenerationParameter


class VoiceMapper(_VoiceMapper):
    name = SpeechGenerationParameter.VOICE


class SpeedMapper(_SpeedMapper):
    name = SpeechGenerationParameter.SPEED


class OutputFormatMapper(_ResponseFormatMapper):
    name = SpeechGenerationParameter.OUTPUT_FORMAT


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
    SpeedMapper(),
    OutputFormatMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
