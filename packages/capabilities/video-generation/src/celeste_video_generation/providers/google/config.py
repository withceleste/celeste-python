"""Google provider configuration for video generation."""

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
GENERATE_ENDPOINT = "/models/{model_id}:predictLongRunning"
POLL_ENDPOINT = "/{operation_name}"
POLL_INTERVAL = 10  # seconds
DEFAULT_TIMEOUT = 300.0  # 5 minutes for long-running operations
STORAGE_BASE_URL = "https://storage.googleapis.com/"
