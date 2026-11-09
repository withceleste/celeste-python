"""TypeSafe provider package for Celeste AI."""

from celeste.core import Provider
from celeste.credentials import register_auth

# Register provider auth config when package is imported.
register_auth(  # nosec B106 - env var name, not hardcoded password
    provider=Provider.TYPESAFE,
    secret_name="TYPESAFE_API_KEY",
    header="Authorization",
    prefix="Bearer ",
)
