"""OpenAI voice definitions for audio modality."""

from celeste.core import Provider

from ...voices import Voice

# Model-specific voice lists
# tts-1 supports: alloy, ash, coral, echo, fable, nova, onyx, sage, shimmer (9 voices, NO ballad)
TTS1_VOICES = [
    Voice(
        id="alloy",
        provider=Provider.OPENAI,
        name="Alloy",
        languages=set(),  # OpenAI voices support multiple languages but don't specify per-voice
    ),
    Voice(
        id="ash",
        provider=Provider.OPENAI,
        name="Ash",
        languages=set(),
    ),
    Voice(
        id="coral",
        provider=Provider.OPENAI,
        name="Coral",
        languages=set(),
    ),
    Voice(
        id="echo",
        provider=Provider.OPENAI,
        name="Echo",
        languages=set(),
    ),
    Voice(
        id="fable",
        provider=Provider.OPENAI,
        name="Fable",
        languages=set(),
    ),
    Voice(
        id="nova",
        provider=Provider.OPENAI,
        name="Nova",
        languages=set(),
    ),
    Voice(
        id="onyx",
        provider=Provider.OPENAI,
        name="Onyx",
        languages=set(),
    ),
    Voice(
        id="sage",
        provider=Provider.OPENAI,
        name="Sage",
        languages=set(),
    ),
    Voice(
        id="shimmer",
        provider=Provider.OPENAI,
        name="Shimmer",
        languages=set(),
    ),
]

# tts-1-hd supports same voices as tts-1 (conservative assumption)
TTS1_HD_VOICES = TTS1_VOICES

# gpt-4o-mini-tts supports all 10 voices including ballad
GPT4O_MINI_TTS_VOICES = [
    Voice(
        id="alloy",
        provider=Provider.OPENAI,
        name="Alloy",
        languages=set(),
    ),
    Voice(
        id="ash",
        provider=Provider.OPENAI,
        name="Ash",
        languages=set(),
    ),
    Voice(
        id="ballad",
        provider=Provider.OPENAI,
        name="Ballad",
        languages=set(),
    ),
    Voice(
        id="coral",
        provider=Provider.OPENAI,
        name="Coral",
        languages=set(),
    ),
    Voice(
        id="echo",
        provider=Provider.OPENAI,
        name="Echo",
        languages=set(),
    ),
    Voice(
        id="fable",
        provider=Provider.OPENAI,
        name="Fable",
        languages=set(),
    ),
    Voice(
        id="nova",
        provider=Provider.OPENAI,
        name="Nova",
        languages=set(),
    ),
    Voice(
        id="onyx",
        provider=Provider.OPENAI,
        name="Onyx",
        languages=set(),
    ),
    Voice(
        id="sage",
        provider=Provider.OPENAI,
        name="Sage",
        languages=set(),
    ),
    Voice(
        id="shimmer",
        provider=Provider.OPENAI,
        name="Shimmer",
        languages=set(),
    ),
]

# Union of all voices for package-level exports
OPENAI_VOICES = GPT4O_MINI_TTS_VOICES

__all__ = [
    "GPT4O_MINI_TTS_VOICES",
    "OPENAI_VOICES",
    "TTS1_HD_VOICES",
    "TTS1_VOICES",
]
