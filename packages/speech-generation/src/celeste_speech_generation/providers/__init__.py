"""Provider implementations for speech generation."""

from celeste import Client, Provider

__all__ = ["PROVIDERS"]


def _get_providers() -> list[tuple[Provider, type[Client]]]:
    """Lazy-load providers."""
    # Import clients directly from .client modules to avoid __init__.py imports
    from celeste_speech_generation.providers.elevenlabs.client import (
        ElevenLabsSpeechGenerationClient,
    )
    from celeste_speech_generation.providers.google.client import (
        GoogleSpeechGenerationClient,
    )
    from celeste_speech_generation.providers.gradium.client import (
        GradiumSpeechGenerationClient,
    )
    from celeste_speech_generation.providers.openai.client import (
        OpenAISpeechGenerationClient,
    )

    return [
        (Provider.GOOGLE, GoogleSpeechGenerationClient),
        (Provider.OPENAI, OpenAISpeechGenerationClient),
        (Provider.ELEVENLABS, ElevenLabsSpeechGenerationClient),
        (Provider.GRADIUM, GradiumSpeechGenerationClient),
    ]


PROVIDERS: list[tuple[Provider, type[Client]]] = _get_providers()
