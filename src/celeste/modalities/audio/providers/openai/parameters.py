"""OpenAI parameter mappers for audio modality."""

from celeste.parameters import ParameterMapper
from celeste.providers.openai.audio.parameters import (
    ResponseFormatMapper as _ResponseFormatMapper,
)
from celeste.providers.openai.audio.parameters import (
    SpeedMapper as _SpeedMapper,
)
from celeste.providers.openai.audio.parameters import (
    VoiceMapper as _VoiceMapper,
)

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


OPENAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
    SpeedMapper(),
    OutputFormatMapper(),
]

__all__ = ["OPENAI_PARAMETER_MAPPERS"]
