"""Core enumerations for Celeste."""

from enum import StrEnum


class Provider(StrEnum):
    """Supported AI providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    COHERE = "cohere"
    XAI = "xai"
    HUGGINGFACE = "huggingface"
    REPLICATE = "replicate"
    STABILITYAI = "stabilityai"
    LUMA = "luma"
    TOPAZLABS = "topazlabs"
    PERPLEXITY = "perplexity"
    BYTEDANCE = "bytedance"
    ELEVENLABS = "elevenlabs"


class Capability(StrEnum):
    """Supported AI capabilities."""

    # Text
    TEXT_GENERATION = "text-generation"
    EMBEDDINGS = "embeddings"

    # Image
    IMAGE_GENERATION = "image-generation"
    IMAGE_INTELLIGENCE = "image-intelligence"

    # Video
    VIDEO_INTELLIGENCE = "video-intelligence"
    VIDEO_GENERATION = "video-generation"

    # Audio
    AUDIO_INTELLIGENCE = "audio-intelligence"

    # Speech
    SPEECH_GENERATION = "speech-generation"

    # Search
    SEARCH = "search"


class Parameter(StrEnum):
    """Universal parameters across most capabilities."""

    TEMPERATURE = "temperature"
    SEED = "seed"
    MAX_TOKENS = "max_tokens"


__all__ = ["Capability", "Parameter", "Provider"]
