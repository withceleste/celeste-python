"""Anthropic max_tokens defaults to the model's output ceiling."""

from celeste.constraints import Range
from celeste.core import Parameter
from celeste.providers.anthropic.messages import config
from tests.unit_tests.conftest import anthropic_test_client


def test_max_tokens_defaults_to_model_ceiling() -> None:
    client = anthropic_test_client({Parameter.MAX_TOKENS: Range(min=1, max=128000)})

    assert client._resolve_max_tokens() == 128000
    assert anthropic_test_client()._resolve_max_tokens() == config.DEFAULT_MAX_TOKENS
