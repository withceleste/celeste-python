"""Decision providers."""

from celeste.core import Provider

from ..client import DecisionClient
from .typesafe import TypeSafeDecisionClient

PROVIDERS: dict[Provider, type[DecisionClient]] = {
    Provider.TYPESAFE: TypeSafeDecisionClient,
}
