"""Integration tests for tool_choice= parameter."""

import pytest

from celeste import Modality, Operation, create_client, list_models
from celeste.modalities.text import TextOutput
from celeste.modalities.text.parameters import TextParameter
from celeste.models import Model

TOOL_CHOICE_MODELS = [
    m
    for m in list_models(modality=Modality.TEXT, operation=Operation.GENERATE)
    if TextParameter.TOOL_CHOICE in m.parameter_constraints
]

WEATHER_TOOL = {
    "name": "get_weather",
    "description": "Get current weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
}


@pytest.mark.parametrize(
    "model",
    TOOL_CHOICE_MODELS,
    ids=lambda m: f"{m.provider}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_tool_choice_required_forces_tool_call(model: Model) -> None:
    """tool_choice='required' forces a tool call even when the prompt doesn't ask for one."""
    client = create_client(modality=Modality.TEXT, model=model)

    output = await client.generate(
        prompt="Hey there, how are you?",
        tools=[WEATHER_TOOL],
        tool_choice="required",
        max_tokens=500,
    )

    assert isinstance(output, TextOutput)
    assert len(output.tool_calls) > 0, (
        f"{model.provider}/{model.id} did not return tool_calls"
    )
    assert output.tool_calls[0].name == "get_weather"
