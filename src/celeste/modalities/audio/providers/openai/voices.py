"""OpenAI voice definitions for audio modality."""

from celeste.core import Provider

from ...voices import Voice

# Snapshot 2026-07-14: 13 built-in voices.
# OpenAI publishes previews, but no text descriptions.
# Source: https://platform.openai.com/docs/api-reference/audio/createSpeech
OPENAI_VOICES = [
    Voice(
        id=voice_id,
        provider=Provider.OPENAI,
        name=voice_id.title(),
    )
    for voice_id in (
        "alloy",
        "ash",
        "ballad",
        "coral",
        "echo",
        "fable",
        "onyx",
        "nova",
        "sage",
        "shimmer",
        "verse",
        "marin",
        "cedar",
    )
]

# tts-1 and tts-1-hd accept only a subset of the built-in voices.
# Source: https://developers.openai.com/api/docs/guides/text-to-speech
TTS1_VOICES = [
    voice
    for voice in OPENAI_VOICES
    if voice.id
    in ("alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer")
]
TTS1_HD_VOICES = TTS1_VOICES
GPT4O_MINI_TTS_VOICES = OPENAI_VOICES

__all__ = [
    "GPT4O_MINI_TTS_VOICES",
    "OPENAI_VOICES",
    "TTS1_HD_VOICES",
    "TTS1_VOICES",
]
