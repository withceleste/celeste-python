"""OpenRouter provider package for Celeste AI."""

from celeste.core import Provider
from celeste.credentials import register_auth

register_auth(  # nosec B106 - env var name, not hardcoded password
    provider=Provider.OPENROUTER,
    secret_name="OPENROUTER_API_KEY",
    header="Authorization",
    prefix="Bearer ",
)
