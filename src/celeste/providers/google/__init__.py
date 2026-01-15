"""Google provider package for Celeste AI."""

from celeste.auth import register_auth
from celeste.core import Provider
from celeste.credentials import register_auth as register_provider_auth

from .auth import GoogleADC

# Register Google with API key auth (for Gemini API)
# Cloud TTS overrides to use ADC in its client
register_provider_auth(
    Provider.GOOGLE,
    secret_name="GOOGLE_API_KEY",  # nosec B106 - env var name, not hardcoded password
    header="x-goog-api-key",
    prefix="",
)

# Legacy string-based lookup
register_auth("google_adc", GoogleADC)
