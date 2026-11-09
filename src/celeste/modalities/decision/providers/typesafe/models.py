"""TypeSafe models for decision modality."""

from celeste.constraints import ImagesConstraint
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import DecisionParameter

MODELS: list[Model] = [
    Model(
        id="jev-latest",
        provider=Provider.TYPESAFE,
        display_name="Jev (Latest)",
        operations={Modality.DECISION: {Operation.DECIDE}},
        parameter_constraints={DecisionParameter.IMAGE: ImagesConstraint()},
    ),
    Model(
        id="jev-preview",
        provider=Provider.TYPESAFE,
        display_name="Jev (Preview)",
        operations={Modality.DECISION: {Operation.DECIDE}},
        parameter_constraints={DecisionParameter.IMAGE: ImagesConstraint()},
    ),
    Model(
        id="jev-1.14.0",
        provider=Provider.TYPESAFE,
        display_name="Jev 1.14",
        operations={Modality.DECISION: {Operation.DECIDE}},
        parameter_constraints={DecisionParameter.IMAGE: ImagesConstraint()},
    ),
    Model(
        id="jev-1.13.0",
        provider=Provider.TYPESAFE,
        display_name="Jev 1.13",
        operations={Modality.DECISION: {Operation.DECIDE}},
        parameter_constraints={DecisionParameter.IMAGE: ImagesConstraint()},
    ),
]
