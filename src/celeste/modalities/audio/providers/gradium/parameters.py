"""Gradium parameter mappers for audio modality."""

from celeste.parameters import ParameterMapper
from celeste.providers.gradium.text_to_speech.parameters import (
    OutputFormatMapper as _OutputFormatMapper,
)
from celeste.providers.gradium.text_to_speech.parameters import (
    VoiceMapper as _VoiceMapper,
)

from ...parameters import AudioParameter


class VoiceMapper(_VoiceMapper):
    """Map voice to Gradium voice_id parameter."""

    name = AudioParameter.VOICE


class OutputFormatMapper(_OutputFormatMapper):
    """Map output_format to Gradium output_format parameter."""

    name = AudioParameter.OUTPUT_FORMAT


GRADIUM_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
    OutputFormatMapper(),
]

__all__ = ["GRADIUM_PARAMETER_MAPPERS"]
