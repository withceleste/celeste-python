"""Anthropic provider configuration for text generation."""

# HTTP Configuration
BASE_URL = "https://api.anthropic.com"
ENDPOINT = "/v1/messages"
STREAM_ENDPOINT = ENDPOINT

# Authentication
AUTH_HEADER_NAME = "x-api-key"
AUTH_HEADER_PREFIX = ""

# API Version Header (required by Anthropic)
ANTHROPIC_VERSION_HEADER = "anthropic-version"
ANTHROPIC_VERSION = "2023-06-01"

# Beta Features
ANTHROPIC_BETA_HEADER = "anthropic-beta"
STRUCTURED_OUTPUTS_BETA = "structured-outputs-2025-11-13"
