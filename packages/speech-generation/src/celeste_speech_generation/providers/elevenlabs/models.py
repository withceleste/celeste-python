"""ElevenLabs models for speech generation."""

from celeste import Model, Provider
from celeste.constraints import Choice, Range
from celeste_speech_generation.constraints import VoiceConstraint
from celeste_speech_generation.parameters import SpeechGenerationParameter

from .voices import ELEVENLABS_VOICES

MODELS: list[Model] = [
    Model(
        id="eleven_v3",
        provider=Provider.ELEVENLABS,
        display_name="Eleven v3",
        streaming=True,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            SpeechGenerationParameter.SPEED: Range(min=0.7, max=1.2),
            SpeechGenerationParameter.RESPONSE_FORMAT: Choice(
                options=[
                    "mp3_44100_128",
                    "pcm_22050_16",
                    "pcm_24000_16",
                    "pcm_44100_16",
                ]
            ),
        },
    ),
    Model(
        id="eleven_multilingual_v2",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Multilingual v2",
        streaming=True,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            SpeechGenerationParameter.SPEED: Range(min=0.7, max=1.2),
            SpeechGenerationParameter.RESPONSE_FORMAT: Choice(
                options=[
                    "mp3_44100_128",
                    "pcm_22050_16",
                    "pcm_24000_16",
                    "pcm_44100_16",
                ]
            ),
        },
    ),
    Model(
        id="eleven_turbo_v2_5",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Turbo v2.5",
        streaming=True,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            SpeechGenerationParameter.SPEED: Range(min=0.7, max=1.2),
            SpeechGenerationParameter.RESPONSE_FORMAT: Choice(
                options=[
                    "mp3_44100_128",
                    "pcm_22050_16",
                    "pcm_24000_16",
                    "pcm_44100_16",
                ]
            ),
        },
    ),
    Model(
        id="eleven_turbo_v2",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Turbo v2",
        streaming=True,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            SpeechGenerationParameter.SPEED: Range(min=0.7, max=1.2),
            SpeechGenerationParameter.RESPONSE_FORMAT: Choice(
                options=[
                    "mp3_44100_128",
                    "pcm_22050_16",
                    "pcm_24000_16",
                    "pcm_44100_16",
                ]
            ),
        },
    ),
    Model(
        id="eleven_flash_v2_5",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Flash v2.5",
        streaming=True,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            SpeechGenerationParameter.SPEED: Range(min=0.7, max=1.2),
            SpeechGenerationParameter.RESPONSE_FORMAT: Choice(
                options=[
                    "mp3_44100_128",
                    "pcm_22050_16",
                    "pcm_24000_16",
                    "pcm_44100_16",
                ]
            ),
        },
    ),
    Model(
        id="eleven_flash_v2",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Flash v2",
        streaming=True,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            SpeechGenerationParameter.SPEED: Range(min=0.7, max=1.2),
            SpeechGenerationParameter.RESPONSE_FORMAT: Choice(
                options=[
                    "mp3_44100_128",
                    "pcm_22050_16",
                    "pcm_24000_16",
                    "pcm_44100_16",
                ]
            ),
        },
    ),
    Model(
        id="eleven_multilingual_v1",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Multilingual v1",
        streaming=True,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            SpeechGenerationParameter.SPEED: Range(min=0.7, max=1.2),
            SpeechGenerationParameter.RESPONSE_FORMAT: Choice(
                options=[
                    "mp3_44100_128",
                    "pcm_22050_16",
                    "pcm_24000_16",
                    "pcm_44100_16",
                ]
            ),
        },
    ),
    Model(
        id="eleven_monolingual_v1",
        provider=Provider.ELEVENLABS,
        display_name="Eleven Monolingual v1",
        streaming=True,
        parameter_constraints={
            SpeechGenerationParameter.VOICE: VoiceConstraint(voices=ELEVENLABS_VOICES),
            SpeechGenerationParameter.SPEED: Range(min=0.7, max=1.2),
            SpeechGenerationParameter.RESPONSE_FORMAT: Choice(
                options=[
                    "mp3_44100_128",
                    "pcm_22050_16",
                    "pcm_24000_16",
                    "pcm_44100_16",
                ]
            ),
        },
    ),
]
