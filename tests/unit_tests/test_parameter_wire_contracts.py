from typing import Any

import pytest
from pydantic import BaseModel

from celeste.artifacts import ImageArtifact
from celeste.mime_types import AudioMimeType, ImageMimeType
from celeste.modalities.audio.parameters import AudioParameter
from celeste.modalities.audio.providers.google import parameters as google_audio
from celeste.modalities.images.parameters import ImageParameter
from celeste.modalities.images.providers.bfl import parameters as bfl
from celeste.modalities.images.providers.google import parameters as google_images
from celeste.modalities.text.parameters import TextParameter
from celeste.modalities.text.protocols.chatcompletions import parameters as chat
from celeste.modalities.text.protocols.chatcompletions.client import (
    ChatCompletionsTextClient,
    ChatCompletionsTextStream,
)
from celeste.modalities.text.providers.anthropic import parameters as anthropic
from celeste.modalities.text.providers.google import parameters as google_text
from celeste.modalities.text.providers.groq import parameters as groq
from celeste.modalities.text.providers.moonshot import parameters as moonshot
from celeste.modalities.text.providers.openai import parameters as openai
from celeste.modalities.videos.parameters import VideoParameter
from celeste.modalities.videos.providers.byteplus import parameters as byteplus
from celeste.modalities.videos.providers.xai import parameters as xai
from celeste.models import Model
from celeste.parameters import ParameterMapper

GOOGLE_VERTEX = google_text.GOOGLE_VERTEX_PARAMETER_MAPPERS
GOOGLE_INTERACTIONS = google_text.GOOGLE_INTERACTIONS_PARAMETER_MAPPERS
IMAGES_VERTEX = google_images.GOOGLE_VERTEX_PARAMETER_MAPPERS
IMAGES_INTERACTIONS = google_images.GOOGLE_INTERACTIONS_PARAMETER_MAPPERS
IMAGES_IMAGEN = google_images.GOOGLE_IMAGEN_PARAMETER_MAPPERS
AUDIO_GOOGLE = google_audio.GOOGLE_PARAMETER_MAPPERS
OPEN = openai.OPENAI_PARAMETER_MAPPERS
CHAT = chat.CHATCOMPLETIONS_PARAMETER_MAPPERS
ANTHROPIC = anthropic.ANTHROPIC_PARAMETER_MAPPERS
MOONSHOT = moonshot.MOONSHOT_PARAMETER_MAPPERS
GROQ = groq.GROQ_PARAMETER_MAPPERS
BYTEPLUS = byteplus.BYTEPLUS_PARAMETER_MAPPERS
XAI = xai.XAI_PARAMETER_MAPPERS
BFL = bfl.BFL_PARAMETER_MAPPERS
T, IP, V, AP = TextParameter, ImageParameter, VideoParameter, AudioParameter
GC = ("generationConfig",)
TC = (*GC, "thinkingConfig")
IC = (*GC, "imageConfig")
GS = (*GC, "responseJsonSchema", "properties", "value", "type")
TF, RF = ("text", "format", "name"), ("response_format", "type")
MODEL = Model(id="wire-test", display_name="Wire test")
IMAGE = ImageArtifact(url="https://example.com/image.png")
LOCAL_IMAGE = ImageArtifact(data=b"frame", mime_type=ImageMimeType.PNG)


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
        (GOOGLE_VERTEX, T.TEMPERATURE, 0.2, (*GC, "temperature"), 0.2),
        (GOOGLE_VERTEX, T.MAX_TOKENS, 80, (*GC, "maxOutputTokens"), 80),
        (
            GOOGLE_VERTEX,
            T.THINKING_BUDGET,
            32,
            TC,
            {"thinkingBudget": 32, "includeThoughts": True},
        ),
        (
            GOOGLE_VERTEX,
            T.THINKING_LEVEL,
            "high",
            TC,
            {"thinkingLevel": "high", "includeThoughts": True},
        ),
        (IMAGES_VERTEX, IP.ASPECT_RATIO, "16:9", (*IC, "aspectRatio"), "16:9"),
        (IMAGES_VERTEX, IP.QUALITY, "2K", (*IC, "imageSize"), "2K"),
        (IMAGES_IMAGEN, IP.ASPECT_RATIO, "16:9", ("parameters", "aspectRatio"), "16:9"),
        (IMAGES_IMAGEN, IP.QUALITY, "2K", ("parameters", "imageSize"), "2K"),
        (IMAGES_IMAGEN, IP.NUM_IMAGES, 2, ("parameters", "sampleCount"), 2),
        (
            AUDIO_GOOGLE,
            AP.VOICE,
            "Kore",
            ("generation_config", "speech_config"),
            [{"voice": "Kore"}],
        ),
        (
            AUDIO_GOOGLE,
            AP.LANGUAGE,
            "en",
            ("generation_config", "speech_config"),
            [{"language": "en-US"}],
        ),
        (
            AUDIO_GOOGLE,
            AP.OUTPUT_FORMAT,
            AudioMimeType.MP3,
            ("response_format", "mime_type"),
            "audio/mp3",
        ),
        (
            GOOGLE_INTERACTIONS,
            T.TEMPERATURE,
            0.2,
            ("generation_config", "temperature"),
            0.2,
        ),
        (
            GOOGLE_INTERACTIONS,
            T.MAX_TOKENS,
            80,
            ("generation_config", "max_output_tokens"),
            80,
        ),
        (
            GOOGLE_INTERACTIONS,
            T.THINKING_LEVEL,
            "high",
            ("generation_config",),
            {"thinking_level": "high", "thinking_summaries": "auto"},
        ),
        (
            IMAGES_INTERACTIONS,
            IP.ASPECT_RATIO,
            "16:9",
            ("response_format", "aspect_ratio"),
            "16:9",
        ),
        (
            IMAGES_INTERACTIONS,
            IP.QUALITY,
            "2K",
            ("response_format", "image_size"),
            "2K",
        ),
        (OPEN, T.TEMPERATURE, 0.4, ("temperature",), 0.4),
        (OPEN, T.MAX_TOKENS, 90, ("max_output_tokens",), 90),
        (OPEN, T.THINKING_BUDGET, "high", ("reasoning", "effort"), "high"),
        (OPEN, T.VERBOSITY, "low", ("text", "verbosity"), "low"),
        (CHAT, T.TEMPERATURE, 0.6, ("temperature",), 0.6),
        (CHAT, T.MAX_TOKENS, 100, ("max_tokens",), 100),
        (CHAT, T.THINKING_BUDGET, "high", ("reasoning_effort",), "high"),
        (ANTHROPIC, T.TEMPERATURE, 0.3, ("temperature",), 0.3),
        (MOONSHOT, T.TEMPERATURE, 0.4, ("temperature",), 0.4),
        (MOONSHOT, T.MAX_TOKENS, 120, ("max_completion_tokens",), 120),
        (MOONSHOT, T.THINKING_BUDGET, "max", ("reasoning_effort",), "max"),
        (GROQ, T.THINKING_BUDGET, "default", ("reasoning_effort",), "default"),
        (XAI, V.FIRST_FRAME, IMAGE, ("image", "url"), IMAGE.url),
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


@pytest.mark.parametrize(
    "mappers",
    [
        GOOGLE_VERTEX,
        IMAGES_VERTEX,
        IMAGES_IMAGEN,
        AUDIO_GOOGLE,
        OPEN,
        CHAT,
        ANTHROPIC,
        MOONSHOT,
        GROQ,
        BYTEPLUS,
        XAI,
        BFL,
    ],
)
def test_none_omits_every_optional_parameter(
    mappers: list[ParameterMapper[Any]],
) -> None:
    assert all(mapper.map({}, None, MODEL) == {} for mapper in mappers)


@pytest.mark.parametrize(
    ("mappers", "schema", "wire", "path", "mapped", "parsed"),
    [
        (GOOGLE_VERTEX, Answer, '{"value":1}', GS, "integer", Answer(value=1)),
        (OPEN, ANSWERS, '{"items":[{"value":2}]}', TF, "answer_list", A2),
        (CHAT, ANSWERS, W3, RF, "json_object", A3),
        (GROQ, ANSWERS, W3, RF, "json_object", A3),
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
    parts = _map(IMAGES_VERTEX, IP.REFERENCE_IMAGES, [IMAGE], request)["contents"][0][
        "parts"
    ]
    assert parts == [
        {"file_data": {"file_uri": IMAGE.url}},
        {"text": "describe"},
    ]


@pytest.mark.parametrize(
    ("mappers", "name", "request_body", "expected_input"),
    [
        (
            IMAGES_INTERACTIONS,
            IP.REFERENCE_IMAGES,
            {
                "input": [
                    {
                        "type": "user_input",
                        "content": [{"type": "text", "text": "describe"}],
                    }
                ]
            },
            [
                {
                    "type": "user_input",
                    "content": [
                        {"type": "image", "uri": IMAGE.url},
                        {"type": "text", "text": "describe"},
                    ],
                }
            ],
        ),
        (
            AUDIO_GOOGLE,
            AP.REFERENCE_IMAGES,
            {"input": "describe"},
            [
                {"type": "text", "text": "describe"},
                {"type": "image", "uri": IMAGE.url},
            ],
        ),
    ],
)
def test_google_interactions_media_joins_input_content(
    mappers: list[ParameterMapper[Any]],
    name: str,
    request_body: dict[str, Any],
    expected_input: list[dict[str, Any]],
) -> None:
    assert _map(mappers, name, [IMAGE], request_body)["input"] == expected_input


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
        (V.REFERENCE_IMAGES, [LOCAL_IMAGE], "reference_image"),
        (V.FIRST_FRAME, LOCAL_IMAGE, "first_frame"),
        (V.LAST_FRAME, LOCAL_IMAGE, "last_frame"),
    ],
)
def test_byteplus_images_have_semantic_roles(
    name: str, value: object, role: str
) -> None:
    image = _map(BYTEPLUS, name, value)["content"][0]
    assert image["role"] == role
    assert image["image_url"]["url"].startswith("data:image/png;base64,")


def test_bfl_reference_images_follow_primary_image_numbering() -> None:
    assert _map(BFL, IP.REFERENCE_IMAGES, [IMAGE]) == {"input_image": IMAGE.url}
    assert _map(
        BFL,
        IP.REFERENCE_IMAGES,
        [IMAGE],
        {"input_image": "primary"},
    ) == {"input_image": "primary", "input_image_2": IMAGE.url}


def test_chat_completions_reasoning_fields() -> None:
    client = ChatCompletionsTextClient.model_construct()
    stream = object.__new__(ChatCompletionsTextStream)

    for field in ("reasoning_content", "reasoning"):
        assert client._parse_reasoning(
            {"choices": [{"message": {field: "thought"}}]}
        ) == ("thought", [])
        assert (
            stream._parse_chunk_reasoning(
                {
                    "object": "chat.completion.chunk",
                    "choices": [{"delta": {field: "thought"}}],
                }
            )
            == "thought"
        )
