"""ElevenLabs voice definitions for speech generation."""

from celeste import Provider
from celeste_speech_generation.voices import Voice

# Common ElevenLabs voices (hardcoded initially)
ELEVENLABS_VOICES = [
    Voice(
        id="21m00Tcm4TlvDq8ikWAM",
        provider=Provider.ELEVENLABS,
        name="Rachel",
        languages=set(),  # ElevenLabs voices support multiple languages but don't specify per-voice
    ),
    Voice(
        id="pNInz6obpgDQGcFmaJgB",
        provider=Provider.ELEVENLABS,
        name="Adam",
        languages=set(),
    ),
    Voice(
        id="EXAVITQu4vr4xnSDxMaL",
        provider=Provider.ELEVENLABS,
        name="Bella",
        languages=set(),
    ),
    Voice(
        id="ErXwobaYiN019PkySvjV",
        provider=Provider.ELEVENLABS,
        name="Antoni",
        languages=set(),
    ),
    Voice(
        id="MF3mGyEYCl7XYWbV9V6O",
        provider=Provider.ELEVENLABS,
        name="Elli",
        languages=set(),
    ),
    Voice(
        id="TxGEqnHWrfWFTfGW9XjX",
        provider=Provider.ELEVENLABS,
        name="Josh",
        languages=set(),
    ),
    Voice(
        id="VR6AewLTigWG4xSOukaG",
        provider=Provider.ELEVENLABS,
        name="Arnold",
        languages=set(),
    ),
    Voice(
        id="pMsXgVXv3BLzUgSXRplE",
        provider=Provider.ELEVENLABS,
        name="Serena",
        languages=set(),
    ),
    Voice(
        id="yoZ06aMxZJJ28mfd3POQ",
        provider=Provider.ELEVENLABS,
        name="Sam",
        languages=set(),
    ),
    Voice(
        id="AZnzlk1XvdvUeBnXmlld",
        provider=Provider.ELEVENLABS,
        name="Domi",
        languages=set(),
    ),
]

__all__ = ["ELEVENLABS_VOICES"]
