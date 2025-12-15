"""OpenAI models for speech generation."""

from celeste import Model, Provider
from celeste.constraints import Choice, Range
from celeste.mime_types import AudioMimeType
from celeste_speech_generation.constraints import VoiceConstraint
from celeste_speech_generation.parameters import SpeechGenerationParameter

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
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=TTS1_VOICES),
            SpeechGenerationParameter.SPEED: Range(min=0.25, max=4.0),
            SpeechGenerationParameter.OUTPUT_FORMAT: Choice(
                options=_RESPONSE_FORMAT_OPTIONS
            ),
        },
    ),
    Model(
        id="tts-1-hd",
        provider=Provider.OPENAI,
        display_name="TTS-1 HD",
        streaming=False,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=TTS1_HD_VOICES),
            SpeechGenerationParameter.SPEED: Range(min=0.25, max=4.0),
            SpeechGenerationParameter.OUTPUT_FORMAT: Choice(
                options=_RESPONSE_FORMAT_OPTIONS
            ),
        },
    ),
    Model(
        id="gpt-4o-mini-tts",
        provider=Provider.OPENAI,
        display_name="GPT-4o Mini TTS",
        streaming=False,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(
                voices=GPT4O_MINI_TTS_VOICES
            ),
            SpeechGenerationParameter.SPEED: Range(min=0.25, max=4.0),
            SpeechGenerationParameter.OUTPUT_FORMAT: Choice(
                options=_RESPONSE_FORMAT_OPTIONS
            ),
        },
    ),
]
