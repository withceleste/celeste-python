"""Provider implementations for text generation."""

from celeste import Client, Provider

__all__ = ["PROVIDERS"]


def _get_providers() -> list[tuple[Provider, type[Client]]]:
    """Lazy-load providers."""
    # Import clients directly from .client modules to avoid __init__.py imports
    from celeste_text_generation.providers.anthropic.client import (
        AnthropicTextGenerationClient,
    )
    from celeste_text_generation.providers.cohere.client import (
        CohereTextGenerationClient,
    )
    from celeste_text_generation.providers.google.client import (
        GoogleTextGenerationClient,
    )
    from celeste_text_generation.providers.mistral.client import (
        MistralTextGenerationClient,
    )
    from celeste_text_generation.providers.openai.client import (
        OpenAITextGenerationClient,
    )

    return [
        (Provider.ANTHROPIC, AnthropicTextGenerationClient),
        (Provider.COHERE, CohereTextGenerationClient),
        (Provider.GOOGLE, GoogleTextGenerationClient),
        (Provider.MISTRAL, MistralTextGenerationClient),
        (Provider.OPENAI, OpenAITextGenerationClient),
    ]


PROVIDERS: list[tuple[Provider, type[Client]]] = _get_providers()
