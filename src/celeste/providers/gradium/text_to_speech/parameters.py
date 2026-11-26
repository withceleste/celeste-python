"""Gradium TextToSpeech API parameter mappers."""

from celeste.artifacts import AudioArtifact
from celeste.parameters import FieldMapper
from celeste.types import AudioContent


class VoiceMapper(FieldMapper[AudioContent]):
    """Map voice to Gradium voice_id field."""

    field = "voice_id"


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
    "VoiceMapper",
]
