"""OpenAI parameter mappers for audio modality."""

from celeste.parameters import ParameterMapper
from celeste.providers.openai.audio.parameters import (
    LanguageMapper as _LanguageMapper,
    PromptMapper as _PromptMapper,
    ResponseFormatMapper as _ResponseFormatMapper,
    SpeedMapper as _SpeedMapper,
    TemperatureMapper as _TemperatureMapper,
    VoiceMapper as _VoiceMapper,
)
from celeste.types import AudioContent

from ...parameters import AudioParameter


class VoiceMapper(_VoiceMapper):
    """Map voice to OpenAI's voice parameter."""

    name = AudioParameter.VOICE


class SpeedMapper(_SpeedMapper):
    """Map speed to OpenAI's speed parameter."""

    name = AudioParameter.SPEED


class OutputFormatMapper(_ResponseFormatMapper):
    """Map output_format to OpenAI's response_format parameter."""

    name = AudioParameter.OUTPUT_FORMAT


class LanguageMapper(_LanguageMapper):
    """Map language to OpenAI's transcription language parameter."""

    name = AudioParameter.LANGUAGE


class PromptMapper(_PromptMapper):
    """Map prompt to OpenAI's transcription prompt parameter."""

    name = AudioParameter.PROMPT


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to OpenAI's transcription temperature parameter."""

    name = AudioParameter.TEMPERATURE


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper[AudioContent]] = [
    VoiceMapper(),
    SpeedMapper(),
    OutputFormatMapper(),
    LanguageMapper(),
    PromptMapper(),
    TemperatureMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
