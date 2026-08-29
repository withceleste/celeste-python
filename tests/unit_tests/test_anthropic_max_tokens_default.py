"""Anthropic model metadata tests."""

from celeste.constraints import Choice, Range, ToolChoiceSupport
from celeste.core import Parameter
from celeste.modalities.text.parameters import TextParameter
from celeste.modalities.text.providers.anthropic.models import (
    DYNAMIC_FILTERING_MODELS,
    MODELS,
)
from celeste.providers.anthropic.messages import config
from tests.unit_tests.conftest import anthropic_test_client


def test_max_tokens_defaults_to_model_ceiling() -> None:
    client = anthropic_test_client({Parameter.MAX_TOKENS: Range(min=1, max=128000)})

    assert client._resolve_max_tokens() == 128000
    assert anthropic_test_client()._resolve_max_tokens() == config.DEFAULT_MAX_TOKENS


def test_claude_5_model_metadata() -> None:
    models = {model.id: model for model in MODELS}
    model_ids = {"claude-mythos-5", "claude-opus-5"}

    for model_id in model_ids:
        constraints = models[model_id].parameter_constraints
        assert constraints[Parameter.MAX_TOKENS] == Range(min=1, max=128000)
        assert constraints[TextParameter.THINKING_LEVEL] == Choice(
            options=["low", "medium", "high", "xhigh", "max"]
        )
        assert isinstance(constraints[TextParameter.TOOL_CHOICE], ToolChoiceSupport)

    assert model_ids <= DYNAMIC_FILTERING_MODELS
