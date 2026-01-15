"""BFL (Black Forest Labs) provider package for Celeste AI."""

from celeste.core import Provider
from celeste.credentials import register_auth

register_auth(  # nosec B106 - env var name, not hardcoded password
    provider=Provider.BFL,
    secret_name="BFL_API_KEY",
    header="x-key",
    prefix="",
)
