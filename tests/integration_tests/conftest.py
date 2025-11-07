"""Shared fixtures for integration tests."""

import pytest
from celeste_text_generation.client import TextGenerationClient

from celeste import Capability, Provider, create_client


@pytest.fixture
def openai_client() -> TextGenerationClient:
    """Create OpenAI client for integration tests."""
    return create_client(  # type: ignore[return-value]
        capability=Capability.TEXT_GENERATION,
        provider=Provider.OPENAI,
    )


@pytest.fixture
def anthropic_client() -> TextGenerationClient:
    """Create Anthropic client for integration tests."""
    return create_client(  # type: ignore[return-value]
        capability=Capability.TEXT_GENERATION,
        provider=Provider.ANTHROPIC,
    )


@pytest.fixture
def google_client() -> TextGenerationClient:
    """Create Google client for integration tests."""
    return create_client(  # type: ignore[return-value]
        capability=Capability.TEXT_GENERATION,
        provider=Provider.GOOGLE,
    )


@pytest.fixture
def mistral_client() -> TextGenerationClient:
    """Create Mistral client for integration tests."""
    return create_client(  # type: ignore[return-value]
        capability=Capability.TEXT_GENERATION,
        provider=Provider.MISTRAL,
    )


@pytest.fixture
def cohere_client() -> TextGenerationClient:
    """Create Cohere client for integration tests."""
    return create_client(  # type: ignore[return-value]
        capability=Capability.TEXT_GENERATION,
        provider=Provider.COHERE,
    )
