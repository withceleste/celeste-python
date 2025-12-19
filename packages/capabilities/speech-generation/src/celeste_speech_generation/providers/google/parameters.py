"""Google Cloud TTS parameter mappers for speech generation."""

from celeste_google.cloud_tts.parameters import (
    AudioEncodingMapper as _AudioEncodingMapper,
)
from celeste_google.cloud_tts.parameters import (
    LanguageMapper as _LanguageMapper,
)
from celeste_google.cloud_tts.parameters import (
    PromptMapper as _PromptMapper,
)
from celeste_google.cloud_tts.parameters import (
    VoiceMapper as _VoiceMapper,
)

from celeste.parameters import ParameterMapper
from celeste_speech_generation.parameters import SpeechGenerationParameter

from .mappings import ENCODING_MAP, LOCALE_MAP


class VoiceMapper(_VoiceMapper):
    name = SpeechGenerationParameter.VOICE


class LanguageMapper(_LanguageMapper):
    name = SpeechGenerationParameter.LANGUAGE
    locale_map = LOCALE_MAP


class PromptMapper(_PromptMapper):
    name = SpeechGenerationParameter.PROMPT


class OutputFormatMapper(_AudioEncodingMapper):
    name = SpeechGenerationParameter.OUTPUT_FORMAT
    encoding_map = ENCODING_MAP


GOOGLE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    VoiceMapper(),
    LanguageMapper(),
    PromptMapper(),
    OutputFormatMapper(),
]

__all__ = ["GOOGLE_PARAMETER_MAPPERS"]
