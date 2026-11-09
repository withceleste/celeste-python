"""IO types for decision modality.

Decision modality handles:
- Decisions about a state (text, JSON, or images + typed questions -> typed answers)
"""

from typing import Literal

from pydantic import BaseModel, Field

from celeste.io import Chunk, FinishReason, Input, Output, Usage
from celeste.types import DecisionContent, DecisionValue


class BooleanQuestion(BaseModel):
    """Yes/no question answered with the probability of yes."""

    type: Literal["boolean"] = "boolean"
    instructions: DecisionValue = None
    criteria: dict[Literal["true", "false"], DecisionValue] | None = None


class ChoiceQuestion(BaseModel):
    """Question answered by picking one named option."""

    type: Literal["choice"] = "choice"
    instructions: DecisionValue = None
    criteria: dict[str, DecisionValue]


class ScoreQuestion(BaseModel):
    """Question answered on an ordered scale of levels, lowest first."""

    type: Literal["score"] = "score"
    instructions: DecisionValue = None
    criteria: list[DecisionValue]


class BoxQuestion(BaseModel):
    """Question answered with the bounding box of a target in an image."""

    type: Literal["box"] = "box"
    instructions: DecisionValue = None


class DecisionInput(Input):
    """Input for decision operations."""

    state: DecisionValue
    questions: dict[str, BooleanQuestion | ChoiceQuestion | ScoreQuestion | BoxQuestion]


class DecisionFinishReason(FinishReason):
    """Decision finish reason."""

    reason: str | None = None
    message: str | None = None


class DecisionUsage(Usage):
    """Decision usage metrics."""

    input_tokens: int | None = None
    output_tokens: int | None = None


class DecisionOutput(Output[DecisionContent]):
    """Output from decision operations."""

    usage: DecisionUsage = Field(default_factory=DecisionUsage)
    finish_reason: DecisionFinishReason | None = None


class DecisionChunk(Chunk[DecisionContent]):
    """Chunk for decision streaming (unused: decision does not stream)."""

    finish_reason: DecisionFinishReason | None = None
    usage: DecisionUsage | None = None


__all__ = [
    "BooleanQuestion",
    "BoxQuestion",
    "ChoiceQuestion",
    "DecisionChunk",
    "DecisionFinishReason",
    "DecisionInput",
    "DecisionOutput",
    "DecisionUsage",
    "ScoreQuestion",
]
