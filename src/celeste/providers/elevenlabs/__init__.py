"""ElevenLabs provider package for Celeste AI."""

from celeste.core import Provider
from celeste.credentials import register_auth

register_auth(  # nosec B106 - env var name, not hardcoded password
    provider=Provider.ELEVENLABS,
    secret_name="ELEVENLABS_API_KEY",
    header="xi-api-key",
    prefix="",
)
