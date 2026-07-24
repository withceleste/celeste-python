"""Topaz Labs provider package for Celeste AI."""

from celeste.core import Provider
from celeste.credentials import register_auth

register_auth(  # nosec B106 - env var name, not hardcoded password
    provider=Provider.TOPAZLABS,
    secret_name="TOPAZ_API_KEY",
    header="X-API-Key",
    prefix="",
)
