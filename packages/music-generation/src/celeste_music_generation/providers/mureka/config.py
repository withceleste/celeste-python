"""Mureka provider configuration for music generation."""

# HTTP Configuration
BASE_URL = "https://api.mureka.ai"

# Endpoints
SONG_GENERATE_ENDPOINT = "/v1/song/generate"
SONG_QUERY_ENDPOINT = "/v1/song/query"
INSTRUMENTAL_GENERATE_ENDPOINT = "/v1/instrumental/generate"
INSTRUMENTAL_QUERY_ENDPOINT = "/v1/instrumental/query"

# Authentication
AUTH_HEADER_NAME = "Authorization"
AUTH_HEADER_PREFIX = "Bearer "

# Polling configuration
DEFAULT_POLL_INTERVAL = 2.0  # seconds
DEFAULT_TIMEOUT = 300.0  # 5 minutes
MAX_POLL_ATTEMPTS = 150  # 150 attempts * 2s = 5 minutes max

# Task statuses
TASK_STATUS_PENDING = "pending"
TASK_STATUS_PROCESSING = "processing"
TASK_STATUS_STREAMING = "streaming"
TASK_STATUS_SUCCEEDED = "succeeded"
TASK_STATUS_FAILED = "failed"

TASK_TERMINAL_STATUSES = {TASK_STATUS_SUCCEEDED, TASK_STATUS_FAILED}

__all__ = [
    "AUTH_HEADER_NAME",
    "AUTH_HEADER_PREFIX",
    "BASE_URL",
    "DEFAULT_POLL_INTERVAL",
    "DEFAULT_TIMEOUT",
    "INSTRUMENTAL_GENERATE_ENDPOINT",
    "INSTRUMENTAL_QUERY_ENDPOINT",
    "MAX_POLL_ATTEMPTS",
    "SONG_GENERATE_ENDPOINT",
    "SONG_QUERY_ENDPOINT",
    "TASK_STATUS_FAILED",
    "TASK_STATUS_PENDING",
    "TASK_STATUS_PROCESSING",
    "TASK_STATUS_STREAMING",
    "TASK_STATUS_SUCCEEDED",
    "TASK_TERMINAL_STATUSES",
]
