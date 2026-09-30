"""OpenAI voice definitions for live modality."""

from celeste.core import Provider
from celeste.modalities.audio.voices import Voice

# gpt-live-1 has its own audio.output.voice enum, including voices absent from TTS.
# Source: https://developers.openai.com/api/reference/resources/live/primary-websocket
OPENAI_LIVE_VOICES = [
    Voice(
        id=voice_id,
        provider=Provider.OPENAI,
        name=voice_id.title(),
    )
    for voice_id in (
        "alloy",
        "ash",
        "ballad",
        "beacon",
        "bossa",
        "cedar",
        "cinder",
        "coral",
        "delta",
        "echo",
        "gleam",
        "marin",
        "meridian",
        "quartz",
        "ripple",
        "sage",
        "shimmer",
        "stone",
        "tempo",
        "verse",
        "vesper",
        "willow",
    )
]

__all__ = ["OPENAI_LIVE_VOICES"]
