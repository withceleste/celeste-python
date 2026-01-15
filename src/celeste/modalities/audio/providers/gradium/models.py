"""Gradium models for audio modality."""

from celeste.constraints import Choice, Range
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...constraints import VoiceConstraint
from ...parameters import AudioParameter
from .voices import GRADIUM_VOICES

MODELS: list[Model] = [
    Model(
        id="default",
        provider=Provider.GRADIUM,
        display_name="Gradium Default TTS",
        streaming=True,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=GRADIUM_VOICES),
            AudioParameter.OUTPUT_FORMAT: Choice(
                options=[
                    "wav",
                    "pcm",
                    "opus",
                    "ulaw_8000",
                    "alaw_8000",
                    "pcm_16000",
                    "pcm_24000",
                ]
            ),
            AudioParameter.SPEED: Range(min=0.25, max=4.0),
        },
    ),
]

__all__ = ["MODELS"]
