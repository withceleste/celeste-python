"""Configuration for Anthropic Messages API."""

from enum import StrEnum


class AnthropicMessagesEndpoint(StrEnum):
    """Endpoints for Anthropic Messages API."""

    CREATE_MESSAGE = "/v1/messages"


class VertexMessagesEndpoint(StrEnum):
    """Endpoints for Anthropic on Vertex AI."""

    CREATE_MESSAGE = "/v1/projects/{project_id}/locations/{location}/publishers/anthropic/models/{model_id}:rawPredict"
    STREAM_MESSAGE = "/v1/projects/{project_id}/locations/{location}/publishers/anthropic/models/{model_id}:streamRawPredict"


BASE_URL = "https://api.anthropic.com"

# Required
ANTHROPIC_VERSION = "2026-10-21"
VERTEX_ANTHROPIC_VERSION = "2026-10-21"

# Header
HEADER_ANTHROPIC_VERSION = "anthropic-version"
HEADER_ANTHROPIC_BETA = "anthropic-beta"

# Beta
BETA_PROMPT_CACHING = "prompt-caching-2024-07-31"
BETA_COMPUTER_USE = "computer-use-2024-10-22"
BETA_PDFS = "pdfs-2024-09-25"
BETA_TOKEN_COUNTING = "token-counting-2024-11-01"  # nosec B105
BETA_MAX_TOKENS_SONNET_3_5 = "max-tokens-3-5-sonnet-2024-07-15"
BETA_STRUCTURED_OUTPUTS = "structured-outputs-2025-11-13"

# Defaults
DEFAULT_MAX_TOKENS = 1024
