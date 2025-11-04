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


class Capability(StrEnum):
    """Supported AI capabilities."""

    # Text
    TEXT_GENERATION = "text_generation"
    EMBEDDINGS = "embeddings"

    # Image
    IMAGE_GENERATION = "image_generation"

    # Video
    VIDEO_INTELLIGENCE = "video_intelligence"
    VIDEO_GENERATION = "video_generation"

    # Audio
    AUDIO_INTELLIGENCE = "audio_intelligence"

    # Search
    SEARCH = "search"


class Parameter(StrEnum):
    """Universal parameters across most capabilities."""

    TEMPERATURE = "temperature"
    SEED = "seed"
    MAX_TOKENS = "max_tokens"


__all__ = ["Capability", "Parameter", "Provider"]
