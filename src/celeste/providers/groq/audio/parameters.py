"""Groq Audio API parameter mappers."""

from celeste.parameters import FieldMapper


class LanguageMapper[Content](FieldMapper[Content]):
    """Map language to Groq language field."""

    field = "language"


class PromptMapper[Content](FieldMapper[Content]):
    """Map prompt to Groq prompt field."""

    field = "prompt"


class TemperatureMapper[Content](FieldMapper[Content]):
    """Map temperature to Groq temperature field."""

    field = "temperature"


__all__ = [
    "LanguageMapper",
    "PromptMapper",
    "TemperatureMapper",
]
