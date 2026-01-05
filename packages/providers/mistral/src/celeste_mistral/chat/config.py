"""Configuration for Mistral Chat API."""

from enum import StrEnum


class MistralChatEndpoint(StrEnum):
    """Endpoints for Mistral Chat API."""

    CREATE_CHAT_COMPLETION = "/v1/chat/completions"
    CREATE_FIM_COMPLETION = "/v1/fim/completions"
    CREATE_AGENT_COMPLETION = "/v1/agents/completions"
    CREATE_EMBEDDING = "/v1/embeddings"
    LIST_MODELS = "/v1/models"
    GET_MODEL = "/v1/models/{model_id}"
    DELETE_MODEL = "/v1/models/{model_id}"
    UPLOAD_FILE = "/v1/files"
    LIST_FILES = "/v1/files"
    GET_FILE = "/v1/files/{file_id}"
    DELETE_FILE = "/v1/files/{file_id}"
    GET_FILE_CONTENT = "/v1/files/{file_id}/content"
    CREATE_FINE_TUNING_JOB = "/v1/fine_tuning/jobs"
    LIST_FINE_TUNING_JOBS = "/v1/fine_tuning/jobs"
    GET_FINE_TUNING_JOB = "/v1/fine_tuning/jobs/{job_id}"
    CANCEL_FINE_TUNING_JOB = "/v1/fine_tuning/jobs/{job_id}/cancel"
    CREATE_BATCH_JOB = "/v1/batch/jobs"
    LIST_BATCH_JOBS = "/v1/batch/jobs"
    GET_BATCH_JOB = "/v1/batch/jobs/{job_id}"
    CANCEL_BATCH_JOB = "/v1/batch/jobs/{job_id}/cancel"
    CREATE_AGENT = "/v1/agents"
    LIST_AGENTS = "/v1/agents"
    GET_AGENT = "/v1/agents/{agent_id}"
    DELETE_AGENT = "/v1/agents/{agent_id}"
    UPDATE_AGENT = "/v1/agents/{agent_id}"
    CREATE_OCR = "/v1/ocr"
    CREATE_MODERATION = "/v1/moderations"
    CREATE_CHAT_MODERATION = "/v1/chat/moderations"


BASE_URL = "https://api.mistral.ai"

# Alternative
CODESTRAL_HOST = "https://codestral.mistral.ai"

# Standard
DEFAULT_CONTENT_TYPE = "application/json"
ACCEPT_HEADER = "application/json"

# Required
FILE_UPLOAD_CONTENT_TYPE = "multipart/form-data"

# Server-Sent
STREAMING_DELIMITER = "data: [DONE]"
