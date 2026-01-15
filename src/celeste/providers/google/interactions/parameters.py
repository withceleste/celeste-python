"""Google Interactions API parameter mappers."""

import base64
import json
from typing import Any, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.artifacts import ImageArtifact
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.types import TextContent


class TemperatureMapper(ParameterMapper):
    """Map temperature to Google Interactions generation_config.temperature field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform temperature into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("generation_config", {})["temperature"] = validated_value
        return request


class MaxOutputTokensMapper(ParameterMapper):
    """Map max_tokens to Google Interactions generation_config.max_output_tokens field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform max_tokens into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("generation_config", {})["max_output_tokens"] = (
            validated_value
        )
        return request


class ThinkingBudgetMapper(ParameterMapper):
    """Map thinking_budget to Interactions generation_config.thinking_config.thinking_budget."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinking_budget into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("generation_config", {}).setdefault("thinking_config", {})[
            "thinking_budget"
        ] = validated_value
        return request


class ThinkingLevelMapper(ParameterMapper):
    """Map thinking_level to Interactions generation_config.thinking_level field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinking_level into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("generation_config", {})["thinking_level"] = validated_value
        return request


class PreviousInteractionIdMapper(ParameterMapper):
    """Map previous_interaction_id for stateful conversations."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Add previous_interaction_id to request for conversation continuity."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["previous_interaction_id"] = validated_value
        return request


class BackgroundMapper(ParameterMapper):
    """Map background mode for long-running operations."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Enable background execution mode."""
        validated_value = self._validate_value(value, model)
        if not validated_value:
            return request

        request["background"] = True
        return request


class GoogleSearchMapper(ParameterMapper):
    """Map google_search to Google Interactions tools field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Add google_search tool to request."""
        validated_value = self._validate_value(value, model)
        if not validated_value:
            return request

        tools = request.setdefault("tools", [])
        tools.append({"type": "google_search"})
        return request


class CodeExecutionMapper(ParameterMapper):
    """Map code_execution to Google Interactions tools field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Enable code execution tool."""
        validated_value = self._validate_value(value, model)
        if not validated_value:
            return request

        tools = request.setdefault("tools", [])
        tools.append({"type": "code_execution"})
        return request


class UrlContextMapper(ParameterMapper):
    """Map url_context to Google Interactions tools field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Enable URL context tool for web page analysis."""
        validated_value = self._validate_value(value, model)
        if not validated_value:
            return request

        tools = request.setdefault("tools", [])
        tools.append({"type": "url_context"})
        return request


class ResponseFormatMapper(ParameterMapper):
    """Map response_format to Google Interactions response_format field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Add response_format (JSON schema) to request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        schema = self._convert_to_google_schema(validated_value)
        request["response_format"] = schema
        return request

    def parse_output(self, content: TextContent, value: object | None) -> TextContent:
        """Parse JSON to BaseModel using Pydantic's TypeAdapter."""
        if value is None:
            return content

        # If content is already a BaseModel, return it unchanged
        if isinstance(content, BaseModel):
            return content
        if isinstance(content, list) and content and isinstance(content[0], BaseModel):
            return content

        parsed = json.loads(content) if isinstance(content, str) else content

        # For list[T], handle various formats Google might return
        origin = get_origin(value)
        if origin is list and isinstance(parsed, dict):
            # Google returns arrays directly in JSON schema, but might wrap in object
            if "items" in parsed:
                parsed = parsed["items"]
            else:
                # If it's a dict but not wrapped, try to extract array values
                parsed = list(parsed.values()) if parsed else []

        return TypeAdapter(value).validate_python(parsed)

    def _convert_to_google_schema(self, output_schema: Any) -> dict[str, Any]:  # noqa: ANN401
        """Convert Pydantic BaseModel or list[BaseModel] to Google JSON Schema format."""
        origin = get_origin(output_schema)
        if origin is list:
            inner_type = get_args(output_schema)[0]
            items_schema = inner_type.model_json_schema()
            defs = items_schema.get("$defs", {})
            items_schema_clean = {k: v for k, v in items_schema.items() if k != "$defs"}
            json_schema = {"type": "array", "items": items_schema_clean}
            if defs:
                json_schema["$defs"] = defs
        else:
            json_schema = output_schema.model_json_schema()

        json_schema = self._remove_unsupported_fields(json_schema)
        return json_schema

    def _remove_unsupported_fields(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Remove unsupported metadata fields from schema."""
        result: dict[str, Any] = {}

        for key, value in schema.items():
            if key == "title":
                continue

            if isinstance(value, dict):
                result[key] = self._remove_unsupported_fields(value)
            elif isinstance(value, list):
                result[key] = [
                    self._remove_unsupported_fields(item)
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[key] = value

        return result


class MediaContentMapper(ParameterMapper):
    """Map reference_images to Google Interactions input content."""

    def _build_image_part(self, image: ImageArtifact) -> dict[str, Any]:
        """Build content part from image artifact."""
        if image.url:
            return {"type": "image", "uri": image.url}
        elif image.data:
            base64_data = (
                base64.b64encode(image.data).decode("utf-8")
                if isinstance(image.data, bytes)
                else image.data
            )
            return {
                "type": "image",
                "data": base64_data,
                "mime_type": image.mime_type,
            }
        elif image.path:
            with open(image.path, "rb") as f:
                image_bytes = f.read()
            base64_data = base64.b64encode(image_bytes).decode("utf-8")
            return {
                "type": "image",
                "data": base64_data,
                "mime_type": image.mime_type,
            }
        else:
            msg = "ImageArtifact must have url, data, or path"
            raise ValueError(msg)

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform reference_images into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Convert list of ImageArtifact to list of image parts
        image_parts = [self._build_image_part(img) for img in validated_value]

        # For Interactions API, input can be an array of content parts
        current_input = request.get("input")
        if isinstance(current_input, str):
            # Convert string input to content array with text and images
            request["input"] = [
                *image_parts,
                {"type": "text", "text": current_input},
            ]
        elif isinstance(current_input, list):
            # Prepend images to existing content array
            request["input"] = [*image_parts, *current_input]
        else:
            # Just add images
            request["input"] = image_parts

        return request


class ResponseModalitiesMapper(ParameterMapper):
    """Map response_modalities for multimodal output generation."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Set response modalities for output (e.g., IMAGE, TEXT)."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["response_modalities"] = validated_value
        return request


class SystemInstructionMapper(ParameterMapper):
    """Map system_instruction for system prompts."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Add system instruction to request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request["system_instruction"] = validated_value
        return request


__all__ = [
    "BackgroundMapper",
    "CodeExecutionMapper",
    "GoogleSearchMapper",
    "MaxOutputTokensMapper",
    "MediaContentMapper",
    "PreviousInteractionIdMapper",
    "ResponseFormatMapper",
    "ResponseModalitiesMapper",
    "SystemInstructionMapper",
    "TemperatureMapper",
    "ThinkingBudgetMapper",
    "ThinkingLevelMapper",
    "UrlContextMapper",
]
