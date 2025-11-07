"""Anthropic provider configuration."""

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
