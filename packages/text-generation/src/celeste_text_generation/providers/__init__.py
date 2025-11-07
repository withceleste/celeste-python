"""Provider implementations for text generation."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from celeste.client import Client
    from celeste.core import Provider

__all__ = ["PROVIDERS"]


def _get_providers() -> list[tuple["Provider", type["Client"]]]:
    """Lazy-load providers."""
    from celeste.core import Provider
    from celeste_text_generation.providers.anthropic import (
        AnthropicTextGenerationClient,
    )
    from celeste_text_generation.providers.cohere import CohereTextGenerationClient
    from celeste_text_generation.providers.google import GoogleTextGenerationClient
    from celeste_text_generation.providers.mistral import MistralTextGenerationClient
    from celeste_text_generation.providers.openai import OpenAITextGenerationClient

    return [
        (Provider.ANTHROPIC, AnthropicTextGenerationClient),
        (Provider.COHERE, CohereTextGenerationClient),
        (Provider.GOOGLE, GoogleTextGenerationClient),
        (Provider.MISTRAL, MistralTextGenerationClient),
        (Provider.OPENAI, OpenAITextGenerationClient),
    ]


PROVIDERS: list[tuple["Provider", type["Client"]]] = _get_providers()
