"""Celeste speech generation capability."""


def register_package() -> None:
    """Register speech generation package (client and models)."""
    from celeste.client import register_client
    from celeste.core import Capability
    from celeste.models import register_models
    from celeste_speech_generation.models import MODELS
    from celeste_speech_generation.providers import PROVIDERS

    for provider, client_class in PROVIDERS:
        register_client(Capability.SPEECH_GENERATION, provider, client_class)

    register_models(MODELS, capability=Capability.SPEECH_GENERATION)


from celeste_speech_generation.io import (  # noqa: E402
    SpeechGenerationChunk,
    SpeechGenerationInput,
    SpeechGenerationOutput,
    SpeechGenerationUsage,
)

# Aggregate voices from all providers (after Voice is imported)
from celeste_speech_generation.providers.elevenlabs.voices import (  # noqa: E402
    ELEVENLABS_VOICES,
)
from celeste_speech_generation.providers.google.voices import (  # noqa: E402
    GOOGLE_VOICES,
)
from celeste_speech_generation.providers.openai.voices import (  # noqa: E402
    OPENAI_VOICES,
)
from celeste_speech_generation.streaming import SpeechGenerationStream  # noqa: E402
from celeste_speech_generation.voices import Voice  # noqa: E402

VOICES: list[Voice] = [
    *GOOGLE_VOICES,
    *OPENAI_VOICES,
    *ELEVENLABS_VOICES,
]

__all__ = [
    "VOICES",
    "SpeechGenerationChunk",
    "SpeechGenerationInput",
    "SpeechGenerationOutput",
    "SpeechGenerationStream",
    "SpeechGenerationUsage",
    "Voice",
    "register_package",
]
