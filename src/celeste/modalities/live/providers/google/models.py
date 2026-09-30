"""Google models for live modality."""

from celeste.constraints import (
    AudioConstraint,
    Choice,
    Constraint,
    ImagesConstraint,
    ToolSupport,
)
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import AudioMimeType
from celeste.modalities.audio.constraints import VoiceConstraint
from celeste.modalities.audio.providers.google.voices import GOOGLE_VOICES
from celeste.models import Model
from celeste.tools import WebSearch

from ...parameters import LiveParameter

_MEDIA_CONSTRAINTS: dict[str, Constraint] = {
    LiveParameter.AUDIO: AudioConstraint(supported_mime_types=[AudioMimeType.PCM]),
    LiveParameter.IMAGE: ImagesConstraint(),
    LiveParameter.REFERENCE_IMAGES: ImagesConstraint(),
    LiveParameter.TOOLS: ToolSupport(tools=[WebSearch]),
}

MODELS: list[Model] = [
    Model(
        id="gemini-3.8-live",
        provider=Provider.GOOGLE,
        display_name="Gemini 3.8 Live",
        streaming=True,
        operations={Modality.LIVE: {Operation.CONNECT}},
        parameter_constraints={
            **_MEDIA_CONSTRAINTS,
            LiveParameter.VOICE: VoiceConstraint(voices=GOOGLE_VOICES),
        },
    ),
    Model(
        id="gemini-3.8-live-extended-thinking",
        provider=Provider.GOOGLE,
        display_name="Gemini 3.8 Live Extended Thinking",
        streaming=True,
        operations={Modality.LIVE: {Operation.CONNECT}},
        parameter_constraints={
            **_MEDIA_CONSTRAINTS,
            LiveParameter.VOICE: VoiceConstraint(voices=GOOGLE_VOICES),
            LiveParameter.THINKING_LEVEL: Choice(options=["LOW", "MEDIUM", "HIGH"]),
        },
    ),
]
