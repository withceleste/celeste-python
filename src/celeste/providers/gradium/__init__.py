"""Gradium provider package for Celeste AI."""

from celeste.core import Provider
from celeste.credentials import register_auth

register_auth(  # nosec B106 - env var name, not hardcoded password
    provider=Provider.GRADIUM,
    secret_name="GRADIUM_API_KEY",
    header="x-api-key",
    prefix="",
)
