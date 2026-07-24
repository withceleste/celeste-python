"""Mistral audio models."""

from celeste.constraints import AudioConstraint, Range
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import AudioMimeType
from celeste.models import Model

from ...parameters import AudioParameter

_MISTRAL_AUDIO_MIME_TYPES = [
    AudioMimeType.FLAC,
    AudioMimeType.MP3,
    AudioMimeType.M4A,
    AudioMimeType.OGG,
    AudioMimeType.WAV,
    AudioMimeType.WEBM,
]

_TRANSCRIBE_CONSTRAINTS = {
    AudioParameter.AUDIO: AudioConstraint(
        supported_mime_types=_MISTRAL_AUDIO_MIME_TYPES
    ),
    AudioParameter.TEMPERATURE: Range(min=0.0, max=1.0),
}

MODELS: list[Model] = [
    Model(
        id="voxtral-mini-2602",
        provider=Provider.MISTRAL,
        display_name="Voxtral Mini Transcribe 2",
        streaming=False,
        operations={Modality.AUDIO: {Operation.TRANSCRIBE}},
        parameter_constraints=_TRANSCRIBE_CONSTRAINTS,
    ),
    Model(
        id="voxtral-mini-latest",
        provider=Provider.MISTRAL,
        display_name="Voxtral Mini Transcribe (Latest)",
        streaming=False,
        operations={Modality.AUDIO: {Operation.TRANSCRIBE}},
        parameter_constraints=_TRANSCRIBE_CONSTRAINTS,
    ),
]
