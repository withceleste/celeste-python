"""ElevenLabs Speech-to-Text API parameter mappers."""

from celeste.parameters import FieldMapper


class LanguageCodeMapper[Content](FieldMapper[Content]):
    """Map language to ElevenLabs language_code field."""

    field = "language_code"


__all__ = [
    "LanguageCodeMapper",
]
