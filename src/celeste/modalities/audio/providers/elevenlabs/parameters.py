"""ElevenLabs parameter mappers for audio modality."""

from celeste.parameters import ParameterMapper
from celeste.providers.elevenlabs.text_to_speech.parameters import (
    LanguageCodeMapper as _LanguageCodeMapper,
)
from celeste.providers.elevenlabs.text_to_speech.parameters import (
    OutputFormatMapper as _OutputFormatMapper,
)
from celeste.providers.elevenlabs.text_to_speech.parameters import (
    SpeedMapper as _SpeedMapper,
)
from celeste.providers.elevenlabs.text_to_speech.parameters import (
    VoiceMapper as _VoiceMapper,
)

from ...parameters import AudioParameter


class VoiceMapper(_VoiceMapper):
    """Map voice to ElevenLabs voice_id parameter."""

    name = AudioParameter.VOICE


class SpeedMapper(_SpeedMapper):
    """Map speed to ElevenLabs voice_settings.speed parameter."""

    name = AudioParameter.SPEED


class OutputFormatMapper(_OutputFormatMapper):
    """Map output_format to ElevenLabs output_format parameter."""

    name = AudioParameter.OUTPUT_FORMAT


class LanguageCodeMapper(_LanguageCodeMapper):
    """Map language to ElevenLabs language_code parameter."""

    name = AudioParameter.LANGUAGE


ELEVENLABS_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
    SpeedMapper(),
    OutputFormatMapper(),
    LanguageCodeMapper(),
]

__all__ = ["ELEVENLABS_PARAMETER_MAPPERS"]
