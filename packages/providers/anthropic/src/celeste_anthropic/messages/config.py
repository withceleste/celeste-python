"""Configuration for Anthropic Messages API."""

from enum import StrEnum


class AnthropicMessagesEndpoint(StrEnum):
    """Endpoints for Anthropic Messages API."""

    CREATE_MESSAGE = "/v1/messages"
    COUNT_MESSAGE_TOKENS = "/v1/messages/count_tokens"
    LIST_MODELS = "/v1/models"
    GET_MODEL = "/v1/models/{model_id}"


BASE_URL = "https://api.anthropic.com"

# Required
ANTHROPIC_VERSION = "2023-06-01"
CONTENT_TYPE_JSON = "application/json"

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

# SSE
SSE_EVENT_MESSAGE_START = "message_start"
SSE_EVENT_CONTENT_BLOCK_START = "content_block_start"
SSE_EVENT_PING = "ping"
SSE_EVENT_CONTENT_BLOCK_DELTA = "content_block_delta"
SSE_EVENT_CONTENT_BLOCK_STOP = "content_block_stop"
SSE_EVENT_MESSAGE_DELTA = "message_delta"
SSE_EVENT_MESSAGE_STOP = "message_stop"
SSE_EVENT_ERROR = "error"
