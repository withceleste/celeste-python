"""TypeSafe parameter mappers for decision."""

from celeste.parameters import ParameterMapper
from celeste.types import DecisionContent

TYPESAFE_PARAMETER_MAPPERS: list[ParameterMapper[DecisionContent]] = []

__all__ = ["TYPESAFE_PARAMETER_MAPPERS"]
