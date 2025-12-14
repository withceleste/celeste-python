"""ElevenLabs voice definitions for speech generation."""

from celeste import Provider
from celeste_speech_generation.voices import Voice

# Common ElevenLabs voices (hardcoded initially)
ELEVENLABS_VOICES = [
    Voice(
        id="pNInz6obpgDQGcFmaJgB",
        provider=Provider.ELEVENLABS,
        name="Adam",
        languages=set(),  # ElevenLabs voices support multiple languages but don't specify per-voice
    ),  # Keep - replacement for Antoni/Arnold
    Voice(
        id="EXAVITQu4vr4xnSDxMaL",
        provider=Provider.ELEVENLABS,
        name="Bella",
        languages=set(),
    ),  # Keep - not being replaced
    Voice(
        id="FGY2WhTYpPnrIDTdsKH5",
        provider=Provider.ELEVENLABS,
        name="Laura",
        languages=set(),
    ),  # NEW - replaces Domi (ID confirmed from API)
    Voice(
        id="NOpBlnGInO9m6vDvFkFC",
        provider=Provider.ELEVENLABS,
        name="Spuds",
        languages=set(),
    ),  # Spuds (Grandpa Spuds Oxley)
    # TODO: Add Janet when available in API (replaces Rachel, Serena, Glinda)
    # TODO: Add Peter when available in API (replaces Elli, Fin)
    # TODO: Add Craig when available in API (replaces Josh, Jeremy)
    # TODO: Add Riley when available in API (replaces Sam, Grace)
]

__all__ = ["ELEVENLABS_VOICES"]
