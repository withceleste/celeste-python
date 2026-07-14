"""Tests for exception message branches with caller-visible context."""

from typing import Any

import pytest

from celeste.exceptions import ClientNotFoundError, ModelNotFoundError


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {"model_id": "gpt-4", "provider": "openai"},
            "Model 'gpt-4' not found for provider openai",
        ),
        ({"model_id": "gpt-4"}, "Model 'gpt-4' not found"),
        (
            {"modality": "text", "provider": "openai"},
            "No model found for modality 'text' with provider openai",
        ),
        ({"modality": "images"}, "No model found for modality 'images'"),
        ({}, "Model not found"),
    ],
)
def test_model_not_found_message(kwargs: dict[str, Any], message: str) -> None:
    assert str(ModelNotFoundError(**kwargs)) == message


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {"modality": "text", "operation": "generate", "provider": "openai"},
            "No client registered for modality 'text', operation 'generate' with provider openai",
        ),
        (
            {"modality": "images", "provider": "openai"},
            "No client registered for modality 'images' with provider openai",
        ),
        ({"modality": "videos"}, "No client registered for modality 'videos'"),
        ({}, "No client registered"),
    ],
)
def test_client_not_found_message(kwargs: dict[str, Any], message: str) -> None:
    assert str(ClientNotFoundError(**kwargs)) == message
