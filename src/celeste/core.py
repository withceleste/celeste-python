"""Core enumerations for Celeste."""

from enum import StrEnum


class Provider(StrEnum):
    """Supported AI providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    BFL = "bfl"
    GOOGLE = "google"
    MISTRAL = "mistral"
    MOONSHOT = "moonshot"
    COHERE = "cohere"
    XAI = "xai"
    DEEPSEEK = "deepseek"
    HUGGINGFACE = "huggingface"
    REPLICATE = "replicate"
    STABILITYAI = "stabilityai"
    LUMA = "luma"
    TOPAZLABS = "topazlabs"
    PERPLEXITY = "perplexity"
    BYTEPLUS = "byteplus"
    ELEVENLABS = "elevenlabs"
    GROQ = "groq"
    GRADIUM = "gradium"
    OPENRESPONSES = "openresponses"
    OLLAMA = "ollama"


class Modality(StrEnum):
    """Supported modalities."""

    TEXT = "text"
    EMBEDDINGS = "embeddings"
    IMAGES = "images"
    VIDEOS = "videos"
    AUDIO = "audio"


class Operation(StrEnum):
    """All operations across all modalities.

    Individual modalities define which subset they support via
    VALID_*_OPERATIONS frozensets and *Operation Literal types.
    """

    GENERATE = "generate"
    EDIT = "edit"
    ANALYZE = "analyze"
    SPEAK = "speak"
    TRANSCRIBE = "transcribe"
    EMBED = "embed"
    UPSCALE = "upscale"


class Capability(StrEnum):
    """Supported AI capabilities.

    .. deprecated::
        Use :class:`Modality` and :class:`Operation` instead.
        This enum is kept for backward compatibility.
    """

    # Text
    TEXT_GENERATION = "text-generation"
    TEXT_EMBEDDINGS = "text-embeddings"

    # Image
    IMAGE_GENERATION = "image-generation"
    IMAGE_INTELLIGENCE = "image-intelligence"
    IMAGE_EDIT = "image-edit"

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


class Domain(StrEnum):
    """Semantic grouping of operations by resource type.

    Domain represents what you work with (input type), while
    Modality represents what you produce (output type).
    """

    TEXT = "text"
    IMAGES = "images"
    AUDIO = "audio"
    VIDEOS = "videos"


# (Domain, Operation) → Modality inference
DOMAIN_OPERATION_TO_MODALITY: dict[tuple[Domain, Operation], Modality] = {
    (Domain.TEXT, Operation.GENERATE): Modality.TEXT,
    (Domain.TEXT, Operation.EMBED): Modality.EMBEDDINGS,
    (Domain.IMAGES, Operation.GENERATE): Modality.IMAGES,
    (Domain.IMAGES, Operation.EDIT): Modality.IMAGES,
    (Domain.IMAGES, Operation.ANALYZE): Modality.TEXT,
    (Domain.AUDIO, Operation.SPEAK): Modality.AUDIO,
    (Domain.AUDIO, Operation.ANALYZE): Modality.TEXT,
    (Domain.VIDEOS, Operation.GENERATE): Modality.VIDEOS,
    (Domain.VIDEOS, Operation.ANALYZE): Modality.TEXT,
}


def infer_modality(domain: Domain, operation: Operation) -> Modality:
    """Infer output modality from domain and operation."""
    key = (domain, operation)
    if key not in DOMAIN_OPERATION_TO_MODALITY:
        msg = f"No modality mapping for domain={domain.value}, operation={operation.value}"
        raise ValueError(msg)
    return DOMAIN_OPERATION_TO_MODALITY[key]


__all__ = [
    "DOMAIN_OPERATION_TO_MODALITY",
    "Capability",
    "Domain",
    "InputType",
    "Modality",
    "Operation",
    "Parameter",
    "Provider",
    "UsageField",
    "infer_modality",
]
