"""Configuration for Groq Chat API."""

from enum import StrEnum


class GroqChatEndpoint(StrEnum):
    """Endpoints for Groq Chat API."""

    CREATE_CHAT_COMPLETION = "/openai/v1/chat/completions"


BASE_URL = "https://api.groq.com"
