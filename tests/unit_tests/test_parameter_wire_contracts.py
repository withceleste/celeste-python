from typing import Any

import pytest
from pydantic import BaseModel

from celeste.artifacts import ImageArtifact
from celeste.exceptions import ValidationError
from celeste.modalities.images.parameters import ImageParameter
from celeste.modalities.images.providers.google import parameters as google_images
from celeste.modalities.text.parameters import TextParameter
from celeste.modalities.text.protocols.chatcompletions import parameters as chat
from celeste.modalities.text.providers.anthropic import parameters as anthropic
from celeste.modalities.text.providers.google import parameters as google_text
from celeste.modalities.text.providers.openai import parameters as openai
from celeste.modalities.videos.parameters import VideoParameter
from celeste.modalities.videos.providers.byteplus import parameters as byteplus
from celeste.models import Model
from celeste.parameters import ParameterMapper

GOOGLE = google_text.GOOGLE_PARAMETER_MAPPERS
GEMINI = google_images.GEMINI_PARAMETER_MAPPERS
OPEN = openai.OPENAI_PARAMETER_MAPPERS
CHAT = chat.CHATCOMPLETIONS_PARAMETER_MAPPERS
ANTHROPIC = anthropic.ANTHROPIC_PARAMETER_MAPPERS
BYTEPLUS = byteplus.BYTEPLUS_PARAMETER_MAPPERS
T, IP, V = TextParameter, ImageParameter, VideoParameter
GC = ("generationConfig",)
TC = (*GC, "thinkingConfig")
IC = (*GC, "imageConfig")
GS = (*GC, "responseJsonSchema", "properties", "value", "type")
TF, RF = ("text", "format", "name"), ("response_format", "type")
MODEL = Model(id="wire-test", display_name="Wire test")
IMAGE = ImageArtifact(url="https://example.com/image.png")


class Answer(BaseModel):
    value: int


ANSWERS = list[Answer]
A2, A3 = [Answer(value=2)], [Answer(value=3)]
W3 = {"items": [{"value": 3}]}


def _mapper(mappers: list[ParameterMapper[Any]], name: str) -> ParameterMapper[Any]:
    return next(mapper for mapper in mappers if mapper.name == name)


def _map(
    mappers: list[ParameterMapper[Any]],
    name: str,
    value: object,
    request: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _mapper(mappers, name).map(
        request if request is not None else {}, value, MODEL
    )


def _at(data: dict[str, Any], path: tuple[str, ...]) -> Any:  # noqa: ANN401
    value: Any = data
    for key in path:
        value = value[key]
    return value


@pytest.mark.parametrize(
    ("mappers", "name", "value", "path", "expected"),
    [
        (GOOGLE, T.TEMPERATURE, 0.2, (*GC, "temperature"), 0.2),
        (GOOGLE, T.MAX_TOKENS, 80, (*GC, "maxOutputTokens"), 80),
        (
            GOOGLE,
            T.THINKING_BUDGET,
            32,
            TC,
            {"thinkingBudget": 32, "includeThoughts": True},
        ),
        (
            GOOGLE,
            T.THINKING_LEVEL,
            "high",
            TC,
            {"thinkingLevel": "high", "includeThoughts": True},
        ),
        (GEMINI, IP.ASPECT_RATIO, "16:9", (*IC, "aspectRatio"), "16:9"),
        (GEMINI, IP.QUALITY, "2K", (*IC, "imageSize"), "2K"),
        (OPEN, T.TEMPERATURE, 0.4, ("temperature",), 0.4),
        (OPEN, T.MAX_TOKENS, 90, ("max_output_tokens",), 90),
        (OPEN, T.THINKING_BUDGET, "high", ("reasoning", "effort"), "high"),
        (OPEN, T.VERBOSITY, "low", ("text", "verbosity"), "low"),
        (CHAT, T.TEMPERATURE, 0.6, ("temperature",), 0.6),
        (CHAT, T.MAX_TOKENS, 100, ("max_tokens",), 100),
    ],
)
def test_scalar_parameters_use_provider_wire_shape(
    mappers: list[ParameterMapper[Any]],
    name: str,
    value: object,
    path: tuple[str, ...],
    expected: object,
) -> None:
    request = _map(mappers, name, value)
    assert _at(request, path) == expected


@pytest.mark.parametrize("mappers", [GOOGLE, GEMINI, OPEN, CHAT, ANTHROPIC, BYTEPLUS])
def test_none_omits_every_optional_parameter(
    mappers: list[ParameterMapper[Any]],
) -> None:
    assert all(mapper.map({}, None, MODEL) == {} for mapper in mappers)


@pytest.mark.parametrize(
    ("mappers", "schema", "wire", "path", "mapped", "parsed"),
    [
        (GOOGLE, Answer, '{"value":1}', GS, "integer", Answer(value=1)),
        (OPEN, ANSWERS, '{"items":[{"value":2}]}', TF, "answer_list", A2),
        (CHAT, ANSWERS, W3, RF, "json_object", A3),
    ],
)
def test_structured_output_maps_and_parses_typed_results(
    mappers: list[ParameterMapper[Any]],
    schema: object,
    wire: object,
    path: tuple[str, ...],
    mapped: object,
    parsed: object,
) -> None:
    mapper = _mapper(mappers, T.OUTPUT_SCHEMA)
    assert _at(mapper.map({}, schema, MODEL), path) == mapped
    assert mapper.parse_output(wire, schema) == parsed


@pytest.mark.parametrize(("mappers", "nested"), [(OPEN, False), (CHAT, True)])
def test_user_tools_use_protocol_function_shape(
    mappers: list[ParameterMapper[Any]], nested: bool
) -> None:
    mapped = _map(mappers, T.TOOLS, [{"name": "lookup", "parameters": Answer}])[
        "tools"
    ][0]
    function = mapped["function"] if nested else mapped
    assert mapped["type"] == "function"
    assert function["name"] == "lookup"
    assert function["parameters"]["properties"]["value"]["type"] == "integer"


def test_google_media_precedes_text_content() -> None:
    request = {"contents": [{"parts": [{"text": "describe"}]}]}
    parts = _map(GEMINI, IP.REFERENCE_IMAGES, [IMAGE], request)["contents"][0]["parts"]
    assert parts == [
        {"file_data": {"file_uri": IMAGE.url}},
        {"text": "describe"},
    ]


@pytest.mark.parametrize(
    ("name", "value", "flag"),
    [
        (V.DURATION, 6, "--duration 6"),
        (V.RESOLUTION, "1080p", "--resolution 1080p"),
        (V.ASPECT_RATIO, "16:9", "--ratio 16:9"),
    ],
)
def test_byteplus_options_are_prompt_flags(name: str, value: object, flag: str) -> None:
    request = {"content": [{"type": "text", "text": "A sunrise"}]}
    text = _map(BYTEPLUS, name, value, request)["content"][0]["text"]
    assert text == f"A sunrise {flag}"


@pytest.mark.parametrize(
    ("name", "value", "role"),
    [
        (V.REFERENCE_IMAGES, [IMAGE], "reference_image"),
        (V.FIRST_FRAME, IMAGE, "first_frame"),
        (V.LAST_FRAME, IMAGE, "last_frame"),
    ],
)
def test_byteplus_images_have_semantic_roles(
    name: str, value: object, role: str
) -> None:
    image = _map(BYTEPLUS, name, value)["content"][0]
    assert image["role"] == role
    assert image["image_url"]["url"] == IMAGE.url


@pytest.mark.parametrize("name", [V.FIRST_FRAME, V.LAST_FRAME])
def test_byteplus_frame_requires_url(name: str) -> None:
    with pytest.raises(ValidationError, match="requires image URL"):
        _map(BYTEPLUS, name, ImageArtifact(data=b"frame"))
