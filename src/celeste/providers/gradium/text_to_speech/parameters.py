"""Gradium TextToSpeech API parameter mappers."""

from typing import Any

from celeste.artifacts import AudioArtifact
from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper
from celeste.types import AudioContent


class VoiceMapper(FieldMapper[AudioContent]):
    """Map voice to Gradium voice_id field."""

    field = "voice_id"


class PaddingBonusMapper(ParameterMapper[AudioContent]):
    """Map padding_bonus to Gradium json_config.padding_bonus field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform padding_bonus into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("json_config", {})["padding_bonus"] = validated_value
        return request


class OutputFormatMapper(FieldMapper[AudioContent]):
    """Map output_format to Gradium output_format field."""

    field = "output_format"

    def parse_output(self, content: AudioContent, value: object | None) -> AudioContent:
        """Apply output_format → MIME type mapping to parsed content."""
        if not isinstance(content, AudioArtifact):
            return content

        from celeste.providers.gradium.text_to_speech.client import (
            GradiumTextToSpeechClient,
        )

        mime_type = GradiumTextToSpeechClient._map_output_format_to_mime_type(
            str(value) if value else None
        )
        return AudioArtifact(data=content.data, mime_type=mime_type)


__all__ = [
    "OutputFormatMapper",
    "PaddingBonusMapper",
    "VoiceMapper",
]
