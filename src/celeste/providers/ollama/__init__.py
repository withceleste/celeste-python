"""Ollama provider for Celeste AI."""

from celeste.auth import NoAuth
from celeste.core import Provider
from celeste.credentials import register_auth

# Register Ollama provider with no-auth.
register_auth(provider=Provider.OLLAMA, auth_class=NoAuth)
