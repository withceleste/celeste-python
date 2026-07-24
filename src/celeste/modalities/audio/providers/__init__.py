"""Audio providers."""

from celeste.core import Provider

from ..client import AudioClient
from .elevenlabs import ElevenLabsAudioClient
from .google import GoogleAudioClient
from .gradium import GradiumAudioClient
from .groq import GroqAudioClient
from .openai import OpenAIAudioClient

PROVIDERS: dict[Provider, type[AudioClient]] = {
    Provider.ELEVENLABS: ElevenLabsAudioClient,
    Provider.GOOGLE: GoogleAudioClient,
    Provider.GRADIUM: GradiumAudioClient,
    Provider.GROQ: GroqAudioClient,
    Provider.OPENAI: OpenAIAudioClient,
}
