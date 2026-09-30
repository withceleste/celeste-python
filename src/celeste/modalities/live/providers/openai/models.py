"""OpenAI models for live modality."""

from celeste.constraints import AudioConstraint, Choice, ToolSupport
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import AudioMimeType
from celeste.modalities.audio.constraints import VoiceConstraint
from celeste.models import Model
from celeste.tools import WebSearch

from ...parameters import LiveParameter
from .voices import OPENAI_LIVE_VOICES

OPENAI_AUDIO_FORMATS = [
    {"type": AudioMimeType.PCM, "rate": 24000},
    {"type": AudioMimeType.PCM, "rate": 16000},
    {"type": AudioMimeType.PCMU, "rate": 8000},
    {"type": AudioMimeType.PCMA, "rate": 8000},
]

MODELS: list[Model] = [
    Model(
        id="gpt-live-1",
        provider=Provider.OPENAI,
        display_name="GPT Live 1",
        streaming=True,
        operations={Modality.LIVE: {Operation.CONNECT}},
        parameter_constraints={
            LiveParameter.VOICE: VoiceConstraint(voices=OPENAI_LIVE_VOICES),
            LiveParameter.AUDIO_FORMAT: Choice(options=OPENAI_AUDIO_FORMATS),
            LiveParameter.AUDIO: AudioConstraint(
                supported_mime_types=[
                    AudioMimeType.PCM,
                    AudioMimeType.PCMU,
                    AudioMimeType.PCMA,
                ]
            ),
            LiveParameter.TOOLS: ToolSupport(tools=[WebSearch]),
        },
    ),
]
