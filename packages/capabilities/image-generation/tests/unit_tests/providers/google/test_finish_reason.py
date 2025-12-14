"""Unit tests for Google image generation finish reason parsing."""

from typing import Any

import pytest
from celeste_image_generation.providers.google.client import GoogleImageGenerationClient
from pydantic import SecretStr

from celeste.core import Capability, Provider
from celeste.models import Model


class TestParseFinishReason:
    """Test _parse_finish_reason method for Google image generation client."""

    @pytest.fixture
    def client(self) -> GoogleImageGenerationClient:
        """Create a Google image generation client for testing."""
        return GoogleImageGenerationClient(
            model=Model(
                id="gemini-2.5-flash-image",
                provider=Provider.GOOGLE,
                display_name="Gemini 2.5 Flash Image",
                capabilities={Capability.IMAGE_GENERATION},
            ),
            provider=Provider.GOOGLE,
            capability=Capability.IMAGE_GENERATION,
            api_key=SecretStr("test-key"),
        )

    @pytest.mark.parametrize(
        ("finish_reason", "finish_message", "expected_reason", "expected_message"),
        [
            ("STOP", None, "STOP", None),
            (
                "PROHIBITED_CONTENT",
                "Content blocked due to policy violation",
                "PROHIBITED_CONTENT",
                "Content blocked due to policy violation",
            ),
            ("PROHIBITED_CONTENT", None, "PROHIBITED_CONTENT", None),
            ("NO_IMAGE", "Prompt too vague", "NO_IMAGE", "Prompt too vague"),
            (
                "SAFETY",
                "Safety filters detected inappropriate content",
                "SAFETY",
                "Safety filters detected inappropriate content",
            ),
        ],
        ids=[
            "stop_without_message",
            "prohibited_content_with_message",
            "prohibited_content_without_message",
            "no_image_with_message",
            "safety_with_message",
        ],
    )
    def test_parse_finish_reason_with_valid_reason(
        self,
        client: GoogleImageGenerationClient,
        finish_reason: str,
        finish_message: str | None,
        expected_reason: str,
        expected_message: str | None,
    ) -> None:
        """Test parsing finish reason with valid finishReason values."""
        # Arrange
        candidate: dict[str, Any] = {"finishReason": finish_reason}
        if finish_message is not None:
            candidate["finishMessage"] = finish_message

        response_data: dict[str, Any] = {
            "candidates": [candidate],
            "usageMetadata": {},
        }

        # Act
        result = client._parse_finish_reason(response_data)

        # Assert
        assert result is not None
        assert result.reason == expected_reason
        assert result.message == expected_message

    @pytest.mark.parametrize(
        "response_data",
        [
            {"candidates": [], "usageMetadata": {}},  # Empty candidates
            {"predictions": [], "usageMetadata": {}},  # No candidates key (Imagen)
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "inlineData": {
                                        "mimeType": "image/png",
                                        "data": "base64data",
                                    }
                                }
                            ]
                        }
                    }
                ],
                "usageMetadata": {},
            },  # Candidate without finishReason
        ],
        ids=[
            "empty_candidates",
            "no_candidates_key",
            "candidate_without_finish_reason",
        ],
    )
    def test_parse_finish_reason_returns_none_for_invalid_input(
        self,
        client: GoogleImageGenerationClient,
        response_data: dict[str, Any],
    ) -> None:
        """Test parsing finish reason returns None for invalid/missing input."""
        # Act
        result = client._parse_finish_reason(response_data)

        # Assert
        assert result is None

    def test_parse_finish_reason_empty_string_finish_reason(
        self, client: GoogleImageGenerationClient
    ) -> None:
        """Test parsing finish reason when finishReason is empty string."""
        # Arrange
        response_data: dict[str, Any] = {
            "candidates": [{"finishReason": ""}],
            "usageMetadata": {},
        }

        # Act
        result = client._parse_finish_reason(response_data)

        # Assert
        # Empty string is falsy, so should return None
        assert result is None

    def test_parse_finish_reason_empty_string_message(
        self, client: GoogleImageGenerationClient
    ) -> None:
        """Test parsing finish reason when finishMessage is empty string."""
        # Arrange
        response_data: dict[str, Any] = {
            "candidates": [
                {
                    "finishReason": "STOP",
                    "finishMessage": "",  # Empty string vs None
                }
            ],
            "usageMetadata": {},
        }

        # Act
        result = client._parse_finish_reason(response_data)

        # Assert
        assert result is not None
        assert result.reason == "STOP"
        # Empty string is preserved (candidate.get("finishMessage") returns "")
        assert result.message == ""
