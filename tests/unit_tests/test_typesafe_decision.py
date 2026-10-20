"""Unit tests for TypeSafe decision request/response wiring."""

from pydantic import SecretStr

from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.modalities.decision.io import (
    BooleanQuestion,
    ChoiceQuestion,
    DecisionInput,
    ScoreQuestion,
)
from celeste.modalities.decision.providers.typesafe.client import (
    TypeSafeDecisionClient,
)
from celeste.models import Model
from celeste.types import BooleanAnswer, ChoiceAnswer, ScoreAnswer


def _client() -> TypeSafeDecisionClient:
    return TypeSafeDecisionClient(
        model=Model(
            id="jev-latest",
            provider=Provider.TYPESAFE,
            display_name="Jev (Latest)",
            operations={Modality.DECISION: {Operation.DECIDE}},
        ),
        auth=AuthHeader(
            secret=SecretStr("test"), header="Authorization", prefix="Bearer "
        ),
    )


def test_init_request_maps_questions_to_wire() -> None:
    state = {"order": {"id": "A-1", "status": "refunded"}}
    request = _client()._init_request(
        DecisionInput(
            state=state,
            questions={
                "refunded": BooleanQuestion(instructions="Is the order refunded?"),
                "passed": BooleanQuestion(
                    instructions="Did the build succeed?",
                    criteria={"true": "exit code 0", "false": "non-zero exit"},
                ),
                "route": ChoiceQuestion(
                    instructions="Route this ticket.",
                    criteria={"billing": "payment problems", "technical": None},
                ),
                "urgency": ScoreQuestion(
                    instructions="How urgent is this?",
                    criteria=["low", "medium", "high"],
                ),
            },
        )
    )
    assert request == {
        "state": state,
        "questions": {
            "refunded": {"type": "noul", "instructions": "Is the order refunded?"},
            "passed": {
                "type": "noul",
                "instructions": "Did the build succeed?",
                "criteria": {"true": "exit code 0", "false": "non-zero exit"},
            },
            "route": {
                "type": "choice",
                "instructions": "Route this ticket.",
                "criteria": {"billing": "payment problems", "technical": None},
            },
            "urgency": {
                "type": "score",
                "instructions": "How urgent is this?",
                "criteria": ["low", "medium", "high"],
            },
        },
    }


def test_parse_content_maps_wire_answers() -> None:
    content = _client()._parse_content(
        {
            "model": "jev-1.13.0",
            "answers": {
                "refunded": {"type": "noul", "noul": 0.97},
                "route": {
                    "type": "choice",
                    "choice": "billing",
                    "probabilities": {"billing": 0.91, "technical": 0.09},
                    "confidence": 0.82,
                },
                "urgency": {
                    "type": "score",
                    "score": 1.7,
                    "legend": {"0": "low", "1": "medium", "2": "high"},
                    "probabilities": {"0": 0.05, "1": 0.2, "2": 0.75},
                    "confidence": 0.6,
                },
            },
            "usage": {"input_tokens": 296, "output_tokens": 20},
        }
    )
    assert content == {
        "refunded": BooleanAnswer(probability=0.97),
        "route": ChoiceAnswer(
            choice="billing",
            probabilities={"billing": 0.91, "technical": 0.09},
            confidence=0.82,
        ),
        "urgency": ScoreAnswer(
            score=1.7, probabilities={0: 0.05, 1: 0.2, 2: 0.75}, confidence=0.6
        ),
    }
