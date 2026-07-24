"""Groq models for audio modality."""

from celeste.constraints import AudioConstraint, Range
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import AudioMimeType
from celeste.models import Model

from ...parameters import AudioParameter

_GROQ_AUDIO_MIME_TYPES = [
    AudioMimeType.FLAC,
    AudioMimeType.MP3,
    AudioMimeType.M4A,
    AudioMimeType.OGG,
    AudioMimeType.WAV,
    AudioMimeType.WEBM,
]

MODELS: list[Model] = [
    Model(
        id="whisper-large-v3-turbo",
        provider=Provider.GROQ,
        display_name="Whisper Large V3 Turbo",
        streaming=False,
        operations={Modality.AUDIO: {Operation.TRANSCRIBE}},
        parameter_constraints={
            AudioParameter.AUDIO: AudioConstraint(
                supported_mime_types=_GROQ_AUDIO_MIME_TYPES
            ),
            AudioParameter.TEMPERATURE: Range(min=0.0, max=1.0),
        },
    ),
    Model(
        id="whisper-large-v3",
        provider=Provider.GROQ,
        display_name="Whisper Large V3",
        streaming=False,
        operations={Modality.AUDIO: {Operation.TRANSCRIBE}},
        parameter_constraints={
            AudioParameter.AUDIO: AudioConstraint(
                supported_mime_types=_GROQ_AUDIO_MIME_TYPES
            ),
            AudioParameter.TEMPERATURE: Range(min=0.0, max=1.0),
        },
    ),
]
