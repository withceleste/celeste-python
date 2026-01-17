"""Text providers."""

from celeste.core import Provider

from ..client import TextClient
from .anthropic import AnthropicTextClient
from .cohere import CohereTextClient
from .deepseek import DeepSeekTextClient
from .google import GoogleTextClient
from .groq import GroqTextClient
from .ollama import OllamaTextClient
from .openresponses import OpenResponsesTextClient
from .mistral import MistralTextClient
from .moonshot import MoonshotTextClient
from .openai import OpenAITextClient
from .xai import XAITextClient

PROVIDERS: dict[Provider, type[TextClient]] = {
    Provider.ANTHROPIC: AnthropicTextClient,
    Provider.COHERE: CohereTextClient,
    Provider.DEEPSEEK: DeepSeekTextClient,
    Provider.GOOGLE: GoogleTextClient,
    Provider.GROQ: GroqTextClient,
    Provider.OLLAMA: OllamaTextClient,
    Provider.OPENRESPONSES: OpenResponsesTextClient,
    Provider.MISTRAL: MistralTextClient,
    Provider.MOONSHOT: MoonshotTextClient,
    Provider.OPENAI: OpenAITextClient,
    Provider.XAI: XAITextClient,
}
