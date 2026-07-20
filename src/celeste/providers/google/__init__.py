"""Google provider package for Celeste AI."""

from celeste.core import Provider
from celeste.credentials import register_auth

# Register Google with API key auth (for Gemini API)
register_auth(
    Provider.GOOGLE,
    secret_name="GOOGLE_API_KEY",  # nosec B106 - env var name, not hardcoded password
    header="x-goog-api-key",
    prefix="",
)
