from typing import Any

import pytest
from pydantic import BaseModel

from celeste.artifacts import ImageArtifact
from celeste.mime_types import AudioMimeType, ImageMimeType
from celeste.modalities.audio.parameters import AudioParameter
from celeste.modalities.audio.providers.elevenlabs import parameters as elevenlabs_audio
from celeste.modalities.audio.providers.google import parameters as google_audio
from celeste.modalities.audio.providers.groq import parameters as groq_audio
from celeste.modalities.audio.providers.mistral import parameters as mistral_audio
from celeste.modalities.audio.providers.openai import parameters as openai_audio
from celeste.modalities.images.parameters import ImageParameter
from celeste.modalities.images.providers.bfl import parameters as bfl
from celeste.modalities.images.providers.google import parameters as google_images
from celeste.modalities.images.providers.topazlabs import parameters as topazlabs
from celeste.modalities.segmentation.parameters import SegmentationParameter
from celeste.modalities.segmentation.providers.fal import parameters as fal
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
from celeste.modalities.videos.providers.google import parameters as google_videos
from celeste.modalities.videos.providers.xai import parameters as xai
from celeste.models import Model
from celeste.parameters import ParameterMapper

GOOGLE_VERTEX = google_text.GOOGLE_VERTEX_PARAMETER_MAPPERS
GOOGLE_INTERACTIONS = google_text.GOOGLE_INTERACTIONS_PARAMETER_MAPPERS
IMAGES_VERTEX = google_images.GOOGLE_VERTEX_PARAMETER_MAPPERS
IMAGES_INTERACTIONS = google_images.GOOGLE_INTERACTIONS_PARAMETER_MAPPERS
IMAGES_IMAGEN = google_images.GOOGLE_IMAGEN_PARAMETER_MAPPERS
AUDIO_GOOGLE = google_audio.GOOGLE_PARAMETER_MAPPERS
AUDIO_GROQ = groq_audio.GROQ_PARAMETER_MAPPERS
AUDIO_OPENAI = openai_audio.OPENAI_PARAMETER_MAPPERS
AUDIO_ELEVENLABS_STT = elevenlabs_audio.ELEVENLABS_SPEECH_TO_TEXT_PARAMETER_MAPPERS
AUDIO_MISTRAL = mistral_audio.MISTRAL_PARAMETER_MAPPERS
VIDEOS_VEO = google_videos.GOOGLE_VEO_PARAMETER_MAPPERS
VIDEOS_INTERACTIONS = google_videos.GOOGLE_INTERACTIONS_PARAMETER_MAPPERS
OPEN = openai.OPENAI_PARAMETER_MAPPERS
CHAT = chat.CHATCOMPLETIONS_PARAMETER_MAPPERS
ANTHROPIC = anthropic.ANTHROPIC_PARAMETER_MAPPERS
MOONSHOT = moonshot.MOONSHOT_PARAMETER_MAPPERS
GROQ = groq.GROQ_PARAMETER_MAPPERS
BYTEPLUS = byteplus.BYTEPLUS_PARAMETER_MAPPERS
XAI = xai.XAI_PARAMETER_MAPPERS
BFL = bfl.BFL_PARAMETER_MAPPERS
TOPAZ = topazlabs.TOPAZLABS_PARAMETER_MAPPERS
FAL = fal.FAL_PARAMETER_MAPPERS
T, IP, V, AP, SP = (
    TextParameter,
    ImageParameter,
    VideoParameter,
    AudioParameter,
    SegmentationParameter,
)
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
        (GOOGLE_VERTEX, T.SEED, 7, (*GC, "seed"), 7),
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
        (VIDEOS_VEO, V.ASPECT_RATIO, "16:9", ("parameters", "aspectRatio"), "16:9"),
        (VIDEOS_VEO, V.RESOLUTION, "1080p", ("parameters", "resolution"), "1080p"),
        (VIDEOS_VEO, V.DURATION, 6, ("parameters", "durationSeconds"), 6),
        (
            VIDEOS_INTERACTIONS,
            V.ASPECT_RATIO,
            "9:16",
            ("response_format", "aspect_ratio"),
            "9:16",
        ),
        (
            VIDEOS_INTERACTIONS,
            V.DURATION,
            5,
            ("response_format", "duration"),
            "5s",
        ),
        (
            VIDEOS_INTERACTIONS,
            V.FIRST_FRAME,
            LOCAL_IMAGE,
            ("generation_config", "video_config", "task"),
            "image_to_video",
        ),
        (
            VIDEOS_INTERACTIONS,
            V.REFERENCE_IMAGES,
            [LOCAL_IMAGE],
            ("generation_config", "video_config", "task"),
            "reference_to_video",
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
        (GOOGLE_INTERACTIONS, T.SEED, 7, ("generation_config", "seed"), 7),
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
        (AUDIO_GROQ, AP.LANGUAGE, "en", ("language",), "en"),
        (AUDIO_GROQ, AP.PROMPT, "Celeste", ("prompt",), "Celeste"),
        (AUDIO_GROQ, AP.TEMPERATURE, 0.0, ("temperature",), 0.0),
        (AUDIO_OPENAI, AP.LANGUAGE, "en", ("language",), "en"),
        (AUDIO_OPENAI, AP.PROMPT, "Celeste", ("prompt",), "Celeste"),
        (AUDIO_OPENAI, AP.TEMPERATURE, 0.0, ("temperature",), 0.0),
        (AUDIO_ELEVENLABS_STT, AP.LANGUAGE, "en", ("language_code",), "en"),
        (AUDIO_MISTRAL, AP.LANGUAGE, "en", ("language",), "en"),
        (AUDIO_MISTRAL, AP.TEMPERATURE, 0.0, ("temperature",), 0.0),
        (XAI, V.FIRST_FRAME, IMAGE, ("image", "url"), IMAGE.url),
        (TOPAZ, IP.OUTPUT_WIDTH, 2048, ("output_width",), 2048),
        (TOPAZ, IP.OUTPUT_HEIGHT, 1536, ("output_height",), 1536),
        (TOPAZ, IP.OUTPUT_FORMAT, "jpeg", ("output_format",), "jpeg"),
        (TOPAZ, IP.CROP_TO_FILL, True, ("crop_to_fill",), True),
        (TOPAZ, IP.FACE_ENHANCEMENT, True, ("face_enhancement",), True),
        (TOPAZ, IP.FACE_ENHANCEMENT_STRENGTH, 0.5, ("face_enhancement_strength",), 0.5),
        (
            TOPAZ,
            IP.FACE_ENHANCEMENT_CREATIVITY,
            0.2,
            ("face_enhancement_creativity",),
            0.2,
        ),
        (TOPAZ, IP.SUBJECT_DETECTION, "all", ("subject_detection",), "all"),
        (TOPAZ, IP.SHARPEN, 0.3, ("sharpen",), 0.3),
        (TOPAZ, IP.DENOISE, 0.4, ("denoise",), 0.4),
        (TOPAZ, IP.STRENGTH, 0.8, ("strength",), 0.8),
        (TOPAZ, IP.FIX_COMPRESSION, 0.6, ("fix_compression",), 0.6),
        (TOPAZ, IP.RECOVERY_STRENGTH, 0.9, ("recovery_strength",), 0.9),
        (TOPAZ, IP.OPACITY, 1.0, ("opacity",), 1.0),
        (TOPAZ, IP.DEBLUR_STRENGTH, 0.5, ("deblur_strength",), 0.5),
        (TOPAZ, IP.DETAIL_STRENGTH, 6.0, ("detail_strength",), 6.0),
        (TOPAZ, IP.DENOISE_STRENGTH, 0.5, ("denoise_strength",), 0.5),
        (TOPAZ, IP.DECOMPRESSION_STRENGTH, 0.4, ("decompression_strength",), 0.4),
        (FAL, SP.MAX_MASKS, 5, ("max_masks",), 5),
        (FAL, SP.INCLUDE_SCORES, True, ("include_scores",), True),
        (FAL, SP.INCLUDE_BOXES, True, ("include_boxes",), True),
        (FAL, SP.RETURN_MULTIPLE_MASKS, True, ("return_multiple_masks",), True),
        (
            FAL,
            SP.POINT_PROMPTS,
            [{"x": 10, "y": 20, "label": 1}],
            ("point_prompts",),
            [{"x": 10, "y": 20, "label": 1}],
        ),
        (
            FAL,
            SP.BOX_PROMPTS,
            [{"x_min": 1, "y_min": 2, "x_max": 3, "y_max": 4}],
            ("box_prompts",),
            [{"x_min": 1, "y_min": 2, "x_max": 3, "y_max": 4}],
        ),
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
        AUDIO_GROQ,
        AUDIO_OPENAI,
        AUDIO_ELEVENLABS_STT,
        AUDIO_MISTRAL,
        VIDEOS_VEO,
        VIDEOS_INTERACTIONS,
        OPEN,
        CHAT,
        ANTHROPIC,
        MOONSHOT,
        GROQ,
        BYTEPLUS,
        XAI,
        BFL,
        TOPAZ,
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
        (
            VIDEOS_INTERACTIONS,
            V.REFERENCE_IMAGES,
            {"input": "describe"},
            [
                {"type": "image", "uri": IMAGE.url},
                {"type": "text", "text": "describe"},
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


def test_google_veo_frames_land_in_instances() -> None:
    request = _map(VIDEOS_VEO, V.FIRST_FRAME, LOCAL_IMAGE)
    request = _map(VIDEOS_VEO, V.LAST_FRAME, LOCAL_IMAGE, request)
    request = _map(VIDEOS_VEO, V.REFERENCE_IMAGES, [LOCAL_IMAGE], request)

    instance = request["instances"][0]
    assert instance["image"]["bytesBase64Encoded"] == LOCAL_IMAGE.get_base64()
    assert instance["lastFrame"]["mimeType"] == "image/png"
    assert instance["referenceImages"][0]["referenceType"] == "asset"


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
