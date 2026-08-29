"""Anthropic max_tokens defaults to the model's output ceiling."""

from celeste.constraints import Range, ToolChoiceSupport
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


def test_anthropic_opus_5_catalog_and_structured_output_support() -> None:
    models = {model.id: model for model in MODELS}

    opus_5 = models["claude-opus-5"]
    max_tokens = opus_5.parameter_constraints[Parameter.MAX_TOKENS]
    assert isinstance(max_tokens, Range) and max_tokens.max == 128000
    assert TextParameter.OUTPUT_SCHEMA in opus_5.parameter_constraints
    assert "claude-opus-5" in DYNAMIC_FILTERING_MODELS
    assert "claude-mythos-5" in models
    assert "claude-mythos-5" in DYNAMIC_FILTERING_MODELS
    assert isinstance(
        models["claude-fable-5"].parameter_constraints[TextParameter.TOOL_CHOICE],
        ToolChoiceSupport,
    )
    assert (
        TextParameter.OUTPUT_SCHEMA
        not in models["claude-opus-4-1"].parameter_constraints
    )
    for model_id in ("claude-opus-4-6", "claude-sonnet-4-6"):
        constraint = models[model_id].parameter_constraints[Parameter.MAX_TOKENS]
        assert isinstance(constraint, Range) and constraint.max == 128000
    assert (
        TextParameter.THINKING_LEVEL in models["claude-opus-4-6"].parameter_constraints
    )
    for model_id in (
        "claude-sonnet-4-5",
        "claude-haiku-4-5",
        "claude-opus-4-1",
        "claude-opus-4-5",
        "claude-opus-4-6",
        "claude-sonnet-4-6",
    ):
        constraint = models[model_id].parameter_constraints[
            TextParameter.THINKING_BUDGET
        ]
        assert isinstance(constraint, Range) and constraint.min == 1024
