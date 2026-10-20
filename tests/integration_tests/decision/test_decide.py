import pytest

from celeste import Modality, Operation, Provider, create_client
from celeste.modalities.decision import (
    BooleanQuestion,
    ChoiceQuestion,
    DecisionOutput,
    DecisionUsage,
    ScoreQuestion,
)
from celeste.types import BooleanAnswer, ChoiceAnswer, ScoreAnswer


@pytest.mark.parametrize(
    ("model",),
    [
        ("jev-latest",),
        ("jev-1.13.0",),
        ("jev-preview",),
    ],
)
async def test_decide(model: str) -> None:
    client = create_client(
        modality=Modality.DECISION,
        operation=Operation.DECIDE,
        provider=Provider.TYPESAFE,
        model=model,
    )

    response = await client.decide(
        {"ticket": "I was charged twice for one order and I want my money back."},
        questions={
            "wants_refund": BooleanQuestion(instructions="Is a refund requested?"),
            "route": ChoiceQuestion(
                instructions="Route this support ticket.",
                criteria={"billing": "payment problems", "shipping": None},
            ),
            "urgency": ScoreQuestion(
                instructions="How urgent is this ticket?",
                criteria=["low", "medium", "high"],
            ),
        },
    )

    assert isinstance(response, DecisionOutput)
    assert isinstance(response.content["wants_refund"], BooleanAnswer)
    assert isinstance(response.content["route"], ChoiceAnswer)
    assert response.content["route"].choice in {"billing", "shipping"}
    assert isinstance(response.content["urgency"], ScoreAnswer)
    assert isinstance(response.usage, DecisionUsage)
