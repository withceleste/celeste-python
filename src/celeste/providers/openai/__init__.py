"""OpenAI provider package for Celeste AI."""

from celeste.core import Provider
from celeste.credentials import register_auth

# Register OpenAI auth config when package is imported
register_auth(  # nosec B106 - env var name, not hardcoded password
    provider=Provider.OPENAI,
    secret_name="OPENAI_API_KEY",
    header="Authorization",
    prefix="Bearer ",
)
