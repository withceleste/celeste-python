"""Parameters for decision modality.

Unified parameters for all decision operations (decide).
Model `parameter_constraints` validates parameter values when defined; unconstrained parameters pass through.
"""

from enum import StrEnum

from celeste.parameters import Parameters


class DecisionParameter(StrEnum):
    """Unified parameter names for decision modality."""

    IMAGE = "image"


class DecisionParameters(Parameters, total=False):
    """Parameters for decision operations."""


__all__ = [
    "DecisionParameter",
    "DecisionParameters",
]
