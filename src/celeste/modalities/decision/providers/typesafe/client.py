"""TypeSafe decision client."""

import base64
import uuid
from typing import Any

from celeste.artifacts import ImageArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.typesafe.system_one import config
from celeste.providers.typesafe.system_one.client import (
    TypeSafeSystemOneClient as TypeSafeSystemOneMixin,
)
from celeste.types import (
    BooleanAnswer,
    BoxAnswer,
    ChoiceAnswer,
    DecisionContent,
    DecisionValue,
    JsonValue,
    ScoreAnswer,
)
from celeste.utils import detect_mime_type

from ...client import DecisionClient
from ...io import BooleanQuestion, DecisionInput
from .parameters import TYPESAFE_PARAMETER_MAPPERS


class TypeSafeDecisionClient(TypeSafeSystemOneMixin, DecisionClient):
    """TypeSafe decision client."""

    _decide_endpoint = config.TypeSafeSystemOneEndpoint.CREATE_DECISION

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[DecisionContent]]:
        return TYPESAFE_PARAMETER_MAPPERS

    def _init_request(self, inputs: DecisionInput) -> dict[str, Any]:
        """Build TypeSafe request, sending each image as a referenced asset."""
        assets: dict[str, dict[str, str]] = {}
        references: dict[int, str] = {}

        def to_wire(value: DecisionValue) -> JsonValue:
            """Replace image artifacts with asset references, one asset per artifact."""
            if isinstance(value, ImageArtifact):
                if id(value) in references:
                    return references[id(value)]
                data = value.get_bytes()
                mime_type = value.mime_type or detect_mime_type(data)
                reference = references[id(value)] = str(uuid.uuid4())
                assets[reference] = {
                    "type": "image",
                    "data_base64": base64.b64encode(data).decode("utf-8"),
                }
                if mime_type is not None:
                    assets[reference]["format"] = mime_type.split("/")[-1]
                return reference
            if isinstance(value, dict):
                return {key: to_wire(item) for key, item in value.items()}
            if isinstance(value, list):
                return [to_wire(item) for item in value]
            return value

        questions: dict[str, Any] = {}
        for name, question in inputs.questions.items():
            wire: dict[str, Any] = {
                "type": "noul"
                if isinstance(question, BooleanQuestion)
                else question.type
            }
            for field in ("instructions", "criteria"):
                value = getattr(question, field, None)
                if value is not None:
                    wire[field] = to_wire(value)
            questions[name] = wire

        request: dict[str, Any] = {
            "state": to_wire(inputs.state),
            "questions": questions,
        }
        if assets:
            request["assets"] = assets
        return request

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> DecisionContent:
        """Parse TypeSafe answers into typed decision answers."""
        answers = super()._parse_content(response_data)
        content: DecisionContent = {}
        for name, answer in answers.items():
            answer_type = answer["type"]
            if answer_type == "noul":
                content[name] = BooleanAnswer(probability=answer["noul"])
            elif answer_type == "choice":
                content[name] = ChoiceAnswer.model_validate(answer)
            elif answer_type == "score":
                content[name] = ScoreAnswer.model_validate(answer)
            elif answer_type == "box":
                content[name] = BoxAnswer.model_validate(answer)
            else:
                msg = f"Unknown TypeSafe answer type: {answer_type}"
                raise ValueError(msg)
        return content


__all__ = ["TypeSafeDecisionClient"]
