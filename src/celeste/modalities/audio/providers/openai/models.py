"""OpenAI models for audio modality."""

from celeste.constraints import Choice, Range
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import AudioMimeType
from celeste.models import Model

from ...constraints import VoiceConstraint
from ...parameters import AudioParameter
from .voices import GPT4O_MINI_TTS_VOICES, TTS1_HD_VOICES, TTS1_VOICES

# Common response format options for all OpenAI TTS models
_RESPONSE_FORMAT_OPTIONS = [
    AudioMimeType.MP3,
    AudioMimeType.OGG,  # Maps to "opus" in OpenAI API
    AudioMimeType.AAC,
    AudioMimeType.FLAC,
]

MODELS: list[Model] = [
    Model(
        id="tts-1",
        provider=Provider.OPENAI,
        display_name="TTS-1",
        streaming=False,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=TTS1_VOICES),
            AudioParameter.SPEED: Range(min=0.25, max=4.0),
            AudioParameter.OUTPUT_FORMAT: Choice(options=_RESPONSE_FORMAT_OPTIONS),
        },
    ),
    Model(
        id="tts-1-hd",
        provider=Provider.OPENAI,
        display_name="TTS-1 HD",
        streaming=False,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=TTS1_HD_VOICES),
            AudioParameter.SPEED: Range(min=0.25, max=4.0),
            AudioParameter.OUTPUT_FORMAT: Choice(options=_RESPONSE_FORMAT_OPTIONS),
        },
    ),
    Model(
        id="gpt-4o-mini-tts",
        provider=Provider.OPENAI,
        display_name="GPT-4o Mini TTS",
        streaming=False,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=GPT4O_MINI_TTS_VOICES),
            AudioParameter.SPEED: Range(min=0.25, max=4.0),
            AudioParameter.OUTPUT_FORMAT: Choice(options=_RESPONSE_FORMAT_OPTIONS),
        },
    ),
]
