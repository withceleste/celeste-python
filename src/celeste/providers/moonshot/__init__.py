"""Moonshot provider package for Celeste AI."""

from celeste.core import Provider
from celeste.credentials import register_auth

# Register Moonshot auth config when package is imported
register_auth(  # nosec B106 - env var name, not hardcoded password
    provider=Provider.MOONSHOT,
    secret_name="MOONSHOT_API_KEY",
    header="Authorization",
    prefix="Bearer ",
)
