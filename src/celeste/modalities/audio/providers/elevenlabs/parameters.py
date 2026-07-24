"""ElevenLabs parameter mappers for audio modality."""

from celeste.parameters import ParameterMapper
from celeste.providers.elevenlabs.speech_to_text.parameters import (
    LanguageCodeMapper as _SpeechToTextLanguageCodeMapper,
)
from celeste.providers.elevenlabs.text_to_speech.parameters import (
    LanguageCodeMapper as _TextToSpeechLanguageCodeMapper,
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
from celeste.types import AudioContent

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


class TextToSpeechLanguageCodeMapper(_TextToSpeechLanguageCodeMapper):
    """Map language to ElevenLabs TTS language_code parameter."""

    name = AudioParameter.LANGUAGE


class SpeechToTextLanguageCodeMapper(_SpeechToTextLanguageCodeMapper):
    """Map language to ElevenLabs STT language_code parameter."""

    name = AudioParameter.LANGUAGE


ELEVENLABS_TEXT_TO_SPEECH_PARAMETER_MAPPERS: list[ParameterMapper[AudioContent]] = [
    VoiceMapper(),
    SpeedMapper(),
    OutputFormatMapper(),
    TextToSpeechLanguageCodeMapper(),
]

ELEVENLABS_SPEECH_TO_TEXT_PARAMETER_MAPPERS: list[ParameterMapper[AudioContent]] = [
    SpeechToTextLanguageCodeMapper(),
]

__all__ = [
    "ELEVENLABS_SPEECH_TO_TEXT_PARAMETER_MAPPERS",
    "ELEVENLABS_TEXT_TO_SPEECH_PARAMETER_MAPPERS",
]
