"""Live providers."""

from celeste.core import Provider

from ..client import LiveClient
from .google import GoogleLiveClient
from .openai import OpenAILiveClient

PROVIDERS: dict[Provider, type[LiveClient]] = {
    Provider.GOOGLE: GoogleLiveClient,
    Provider.OPENAI: OpenAILiveClient,
}
