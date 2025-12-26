"""Core enumerations for Celeste."""

from enum import StrEnum


class Provider(StrEnum):
    """Supported AI providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    BFL = "bfl"
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
    BYTEPLUS = "byteplus"
    ELEVENLABS = "elevenlabs"
    GRADIUM = "gradium"


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


class InputType(StrEnum):
    """Input types for capabilities."""

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class Parameter(StrEnum):
    """Universal parameters across most capabilities."""

    TEMPERATURE = "temperature"
    SEED = "seed"
    MAX_TOKENS = "max_tokens"


class UsageField(StrEnum):
    """Standard usage field names across Celeste capabilities.

    Use these when mapping provider usage fields to unified names.
    """

    INPUT_TOKENS = "input_tokens"
    OUTPUT_TOKENS = "output_tokens"
    TOTAL_TOKENS = "total_tokens"
    CACHED_TOKENS = "cached_tokens"
    REASONING_TOKENS = "reasoning_tokens"
    BILLED_TOKENS = "billed_tokens"
    NUM_IMAGES = "num_images"
    BILLED_UNITS = "billed_units"
    INPUT_MP = "input_mp"
    OUTPUT_MP = "output_mp"
    CACHE_CREATION_INPUT_TOKENS = "cache_creation_input_tokens"
    CACHE_READ_INPUT_TOKENS = "cache_read_input_tokens"


__all__ = ["Capability", "InputType", "Parameter", "Provider", "UsageField"]
