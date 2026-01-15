"""ElevenLabs models for audio modality."""

from celeste.constraints import Choice, Range
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...constraints import VoiceConstraint
from ...languages import Language
from ...parameters import AudioParameter
from .voices import ELEVENLABS_VOICES

# Valid output formats for ElevenLabs API
ELEVENLABS_OUTPUT_FORMATS = [
    "mp3_22050_32",
    "mp3_44100_32",
    "mp3_44100_64",
    "mp3_44100_96",
    "mp3_44100_128",
    "mp3_44100_192",
    "pcm_8000",
    "pcm_16000",
    "pcm_22050",
    "pcm_24000",
    "pcm_44100",
    "pcm_48000",
    "ulaw_8000",
    "alaw_8000",
    "opus_48000_32",
    "opus_48000_64",
    "opus_48000_96",
    "opus_48000_128",
    "opus_48000_192",
]

MODELS: list[Model] = [
    Model(
        id="eleven_v3",
        provider=Provider.ELEVENLABS,
        display_name="Eleven v3 (Alpha)",
        streaming=False,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            AudioParameter.SPEED: Range(min=0.7, max=1.2),
            AudioParameter.OUTPUT_FORMAT: Choice(options=ELEVENLABS_OUTPUT_FORMATS),
        },
    ),
    Model(
        id="eleven_multilingual_v2",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Multilingual v2",
        streaming=False,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            AudioParameter.SPEED: Range(min=0.7, max=1.2),
            AudioParameter.OUTPUT_FORMAT: Choice(options=ELEVENLABS_OUTPUT_FORMATS),
        },
    ),
    Model(
        id="eleven_turbo_v2_5",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Turbo v2.5",
        streaming=True,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            AudioParameter.SPEED: Range(min=0.7, max=1.2),
            AudioParameter.LANGUAGE: Choice(options=list(Language)),
            AudioParameter.OUTPUT_FORMAT: Choice(options=ELEVENLABS_OUTPUT_FORMATS),
        },
    ),
    Model(
        id="eleven_turbo_v2",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Turbo v2",
        streaming=True,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            AudioParameter.SPEED: Range(min=0.7, max=1.2),
            AudioParameter.OUTPUT_FORMAT: Choice(options=ELEVENLABS_OUTPUT_FORMATS),
        },
    ),
    Model(
        id="eleven_flash_v2_5",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Flash v2.5",
        streaming=True,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            AudioParameter.SPEED: Range(min=0.7, max=1.2),
            AudioParameter.LANGUAGE: Choice(options=list(Language)),
            AudioParameter.OUTPUT_FORMAT: Choice(options=ELEVENLABS_OUTPUT_FORMATS),
        },
    ),
    Model(
        id="eleven_flash_v2",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Flash v2",
        streaming=True,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            AudioParameter.SPEED: Range(min=0.7, max=1.2),
            AudioParameter.OUTPUT_FORMAT: Choice(options=ELEVENLABS_OUTPUT_FORMATS),
        },
    ),
    Model(
        id="eleven_multilingual_v1",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Multilingual v1",
        streaming=True,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            AudioParameter.SPEED: Range(min=0.7, max=1.2),
            AudioParameter.OUTPUT_FORMAT: Choice(options=ELEVENLABS_OUTPUT_FORMATS),
        },
    ),
    Model(
        id="eleven_monolingual_v1",
        provider=Provider.ELEVENLABS,
        display_name="Eleven English v1",
        streaming=True,
        operations={Modality.AUDIO: {Operation.SPEAK}},
        parameter_constraints={
            AudioParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            AudioParameter.SPEED: Range(min=0.7, max=1.2),
            AudioParameter.OUTPUT_FORMAT: Choice(options=ELEVENLABS_OUTPUT_FORMATS),
        },
    ),
]
