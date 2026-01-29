"""Images providers."""

from celeste.core import Provider

from ..client import ImagesClient
from .bfl import BFLImagesClient
from .byteplus import BytePlusImagesClient
from .google import GoogleImagesClient
from .ollama import OllamaImagesClient
from .openai import OpenAIImagesClient
from .xai import XAIImagesClient

PROVIDERS: dict[Provider, type[ImagesClient]] = {
    Provider.BFL: BFLImagesClient,
    Provider.BYTEPLUS: BytePlusImagesClient,
    Provider.GOOGLE: GoogleImagesClient,
    Provider.OLLAMA: OllamaImagesClient,
    Provider.OPENAI: OpenAIImagesClient,
    Provider.XAI: XAIImagesClient,
}
