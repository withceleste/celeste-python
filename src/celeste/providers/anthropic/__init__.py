"""Anthropic provider package for Celeste AI."""

from celeste.core import Provider
from celeste.credentials import register_auth

# Register Anthropic auth config when package is imported
register_auth(  # nosec B106 - env var name, not hardcoded password
    provider=Provider.ANTHROPIC,
    secret_name="ANTHROPIC_API_KEY",
    header="x-api-key",
    prefix="",
)
