"""Google models for audio modality."""

from celeste.constraints import AudioConstraint, Choice, ImagesConstraint, Str
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import AudioMimeType
from celeste.models import Model

from ...constraints import VoiceConstraint
from ...parameters import AudioParameter
from .voices import GOOGLE_SUPPORTED_LANGUAGES, GOOGLE_VOICES

# Supported output formats for Google TTS
GOOGLE_SUPPORTED_FORMATS = [
    AudioMimeType.MP3,
    AudioMimeType.WAV,
    AudioMimeType.OGG,
    AudioMimeType.PCM,
]

GOOGLE_TRANSCRIBE_FORMATS = [
    AudioMimeType.WAV,
    AudioMimeType.MP3,
    AudioMimeType.AIFF,
    AudioMimeType.AAC,
    AudioMimeType.OGG,
    AudioMimeType.FLAC,
    AudioMimeType.M4A,
    AudioMimeType.PCM,
    AudioMimeType.OPUS,
    AudioMimeType.ALAW,
    AudioMimeType.MULAW,
    AudioMimeType.WEBM,
]

MODELS: list[Model] = [
    Model(
        id="gemini-2.5-flash-preview-tts",
        provider=Provider.GOOGLE,
        display_name="Google TTS Gemini 2.5 Flash (Preview)",
        streaming=False,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=GOOGLE_VOICES),
            AudioParameter.LANGUAGE: Choice(options=GOOGLE_SUPPORTED_LANGUAGES),
            AudioParameter.OUTPUT_FORMAT: Choice(options=GOOGLE_SUPPORTED_FORMATS),
        },
    ),
    Model(
        id="gemini-2.5-pro-preview-tts",
        provider=Provider.GOOGLE,
        display_name="Google TTS Gemini 2.5 Pro (Preview)",
        streaming=False,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=GOOGLE_VOICES),
            AudioParameter.LANGUAGE: Choice(options=GOOGLE_SUPPORTED_LANGUAGES),
            AudioParameter.OUTPUT_FORMAT: Choice(options=GOOGLE_SUPPORTED_FORMATS),
        },
    ),
    Model(
        id="gemini-3.1-flash-tts-preview",
        provider=Provider.GOOGLE,
        display_name="Google TTS Gemini 3.1 Flash (Preview)",
        streaming=True,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=GOOGLE_VOICES),
            AudioParameter.LANGUAGE: Choice(options=GOOGLE_SUPPORTED_LANGUAGES),
            AudioParameter.OUTPUT_FORMAT: Choice(options=GOOGLE_SUPPORTED_FORMATS),
        },
    ),
    Model(
        id="gemini-3.5-transcribe",
        provider=Provider.GOOGLE,
        display_name="Gemini 3.5 Transcribe",
        streaming=False,
        operations={Modality.AUDIO: {Operation.TRANSCRIBE}},
        parameter_constraints={
            AudioParameter.AUDIO: AudioConstraint(
                supported_mime_types=GOOGLE_TRANSCRIBE_FORMATS
            ),
            AudioParameter.LANGUAGE: Str(),
        },
    ),
    Model(
        id="lyria-3-clip-preview",
        provider=Provider.GOOGLE,
        display_name="Google Lyria 3 Clip (Preview)",
        operations={Modality.AUDIO: {Operation.GENERATE}},
        parameter_constraints={
            AudioParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=10),
        },
    ),
    Model(
        id="lyria-3-pro-preview",
        provider=Provider.GOOGLE,
        display_name="Google Lyria 3 Pro (Preview)",
        operations={Modality.AUDIO: {Operation.GENERATE}},
        parameter_constraints={
            AudioParameter.REFERENCE_IMAGES: ImagesConstraint(max_count=10),
        },
    ),
]
