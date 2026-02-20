"""OpenResponses provider for text modality."""

from celeste.auth import NoAuth
from celeste.core import Provider
from celeste.credentials import register_auth

from .client import OpenResponsesTextClient

register_auth(provider=Provider.OPENRESPONSES, auth_class=NoAuth)

__all__ = ["OpenResponsesTextClient"]
