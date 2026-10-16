"""Videos providers."""

from celeste.core import Provider

from ..client import VideosClient
from .bfl import BFLVideosClient
from .byteplus import BytePlusVideosClient
from .google import GoogleVideosClient
from .openai import OpenAIVideosClient
from .xai import XAIVideosClient

PROVIDERS: dict[Provider, type[VideosClient]] = {
    Provider.BFL: BFLVideosClient,
    Provider.BYTEPLUS: BytePlusVideosClient,
    Provider.GOOGLE: GoogleVideosClient,
    Provider.OPENAI: OpenAIVideosClient,
    Provider.XAI: XAIVideosClient,
}
