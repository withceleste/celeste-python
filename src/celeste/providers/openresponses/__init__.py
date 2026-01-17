"""OpenResponses provider for Celeste AI."""

from celeste.auth import NoAuth
from celeste.core import Provider
from celeste.credentials import register_auth

# Register OpenResponses provider with no-auth.
register_auth(provider=Provider.OPENRESPONSES, auth_class=NoAuth)
