import pytest
from pydantic import BaseModel, ValidationError

from celeste.artifacts import (
    AudioArtifact,
    DocumentArtifact,
    ImageArtifact,
    VideoArtifact,
)
from celeste.constraints import (
    AudioConstraint,
    AudiosConstraint,
    Bool,
    Choice,
    Dimensions,
    DocumentConstraint,
    DocumentsConstraint,
    Float,
    ImageConstraint,
    ImagesConstraint,
    Int,
    Pattern,
    Range,
    Schema,
    Str,
    ToolSupport,
    VideoConstraint,
    VideosConstraint,
)
from celeste.exceptions import ConstraintViolationError
from celeste.mime_types import (
    AudioMimeType,
    DocumentMimeType,
    ImageMimeType,
    VideoMimeType,
)
from celeste.tools import WebSearch, XSearch


def test_choice_contract() -> None:
    choice = Choice[str](options=["a", "b"])
    assert choice("b") == "b"
    with pytest.raises(ConstraintViolationError, match="Must be one of"):
        choice("c")
    with pytest.raises(ValidationError):
        Choice[str](options=[])


@pytest.mark.parametrize(
    ("constraint", "values"),
    [
        (Range(min=0, max=10), [0, 5.5, 10]),
        (Range(min=5, max=15, step=3), [5, 8, 14]),
        (Range(min=0.0, max=2.0, step=0.1), [0.1 + 0.1 + 0.1, 0.7]),
        (Range(min=0, max=10, special_values=[-1, 100]), [-1, 5, 100]),
    ],
)
def test_range_accepts_contract_values(constraint: Range, values: list[float]) -> None:
    assert [constraint(value) for value in values] == pytest.approx(values)


@pytest.mark.parametrize(
    ("constraint", "value", "message"),
    [
        (Range(min=0, max=10), "5", "Must be numeric"),
        (Range(min=0, max=10), -1, "Must be between"),
        (Range(min=0, max=10), 11, "Must be between"),
        (Range(min=0, max=10, step=2), 3, "match step"),
        (Range(min=0, max=10, special_values=[-1]), -2, "Must be between"),
    ],
)
def test_range_rejects_invalid_values(
    constraint: Range, value: object, message: str
) -> None:
    with pytest.raises(ConstraintViolationError, match=message):
        constraint(value)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("constraint", "valid", "invalid"),
    [
        (Pattern(pattern=r"\d{3}-\d{4}"), "123-4567", "abc"),
        (Str(min_length=2, max_length=5), "valid", "x"),
        (Str(max_length=3), "abc", "long"),
    ],
)
def test_string_constraints(
    constraint: Pattern | Str, valid: str, invalid: str
) -> None:
    assert constraint(valid) == valid
    with pytest.raises(ConstraintViolationError):
        constraint(invalid)
    with pytest.raises(ConstraintViolationError, match="Must be string"):
        constraint(1)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("constraint", "value", "expected"),
    [
        (Int(), 42, 42),
        (Int(), 42.0, 42),
        (Int(), "-42", -42),
        (Int(), True, True),
        (Float(), 3, 3.0),
        (Float(), 3.5, 3.5),
        (Bool(), True, True),
    ],
)
def test_scalar_constraints_accept_and_normalize(
    constraint: Int | Float | Bool, value: object, expected: object
) -> None:
    assert constraint(value) == expected  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("constraint", "value"),
    [
        (Int(), 1.5),
        (Int(), "one"),
        (Float(), True),
        (Float(), "1.0"),
        (Bool(), 1),
        (Bool(), "true"),
    ],
)
def test_scalar_constraints_reject_invalid_types(
    constraint: Int | Float | Bool, value: object
) -> None:
    with pytest.raises(ConstraintViolationError):
        constraint(value)  # type: ignore[arg-type]


class Payload(BaseModel):
    value: int


@pytest.mark.parametrize("value", [Payload, list[Payload]])
def test_schema_accepts_pydantic_models(value: object) -> None:
    assert Schema()(value) == value  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [str, list[str]])
def test_schema_rejects_other_types(value: object) -> None:
    with pytest.raises(ConstraintViolationError):
        Schema()(value)  # type: ignore[arg-type]


def test_dimensions_parse_presets_and_bounds() -> None:
    constraint = Dimensions(
        min_pixels=100,
        max_pixels=10_000,
        min_aspect_ratio=0.5,
        max_aspect_ratio=2,
        presets={"square": "20x20"},
    )
    assert constraint("square") == "20x20"
    assert constraint("10X20") == "10x20"


def test_dimensions_enforce_multiples() -> None:
    constraint = Dimensions(
        min_pixels=100,
        max_pixels=10_000,
        min_aspect_ratio=0.5,
        max_aspect_ratio=2,
        multiple_of=16,
    )
    assert constraint("16x32") == "16x32"
    with pytest.raises(ConstraintViolationError, match="multiples of 16"):
        constraint("20x32")


@pytest.mark.parametrize("value", [1, "20", "axb", "0x20", "5x5", "10x100"])
def test_dimensions_reject_invalid_values(value: object) -> None:
    constraint = Dimensions(
        min_pixels=100,
        max_pixels=10_000,
        min_aspect_ratio=0.5,
        max_aspect_ratio=2,
    )
    with pytest.raises(ConstraintViolationError):
        constraint(value)  # type: ignore[arg-type]


MEDIA_CASES = [
    (
        ImageConstraint,
        ImagesConstraint,
        ImageArtifact,
        ImageMimeType.PNG,
        ImageMimeType.JPEG,
    ),
    (
        VideoConstraint,
        VideosConstraint,
        VideoArtifact,
        VideoMimeType.MP4,
        VideoMimeType.MOV,
    ),
    (
        AudioConstraint,
        AudiosConstraint,
        AudioArtifact,
        AudioMimeType.MP3,
        AudioMimeType.WAV,
    ),
    (
        DocumentConstraint,
        DocumentsConstraint,
        DocumentArtifact,
        DocumentMimeType.PDF,
        DocumentMimeType.TXT,
    ),
]


@pytest.mark.parametrize(
    ("constraint_type", "_plural", "artifact_type", "valid_mime", "invalid_mime"),
    MEDIA_CASES,
)
def test_single_media_constraints(
    constraint_type: type,
    _plural: type,
    artifact_type: type,
    valid_mime: object,
    invalid_mime: object,
) -> None:
    valid = artifact_type(data=b"data", mime_type=valid_mime)
    invalid = artifact_type(data=b"data", mime_type=invalid_mime)
    constraint = constraint_type(supported_mime_types=[valid_mime])

    assert constraint(valid) is valid
    assert constraint_type()(invalid) is invalid
    for value in ([valid], "not an artifact", invalid):
        with pytest.raises(ConstraintViolationError):
            constraint(value)


@pytest.mark.parametrize(
    ("_single", "constraint_type", "artifact_type", "valid_mime", "invalid_mime"),
    MEDIA_CASES,
)
def test_plural_media_constraints(
    _single: type,
    constraint_type: type,
    artifact_type: type,
    valid_mime: object,
    invalid_mime: object,
) -> None:
    first = artifact_type(data=b"1", mime_type=valid_mime)
    second = artifact_type(data=b"2", mime_type=valid_mime)
    constraint = constraint_type(supported_mime_types=[valid_mime], max_count=2)

    assert constraint(first) == [first]
    assert constraint([first, second]) == [first, second]
    assert constraint([]) == []
    for value in (
        [first, second, first],
        [first, "not an artifact"],
        [first, artifact_type(data=b"bad", mime_type=invalid_mime)],
    ):
        with pytest.raises(ConstraintViolationError):
            constraint(value)


def test_tool_support_allows_custom_and_registered_tools() -> None:
    constraint = ToolSupport(tools=[WebSearch])
    value = [WebSearch(), {"name": "custom"}]
    assert constraint(value) is value
    with pytest.raises(ConstraintViolationError, match="XSearch"):
        constraint([XSearch()])


def test_tool_support_can_reject_custom_tools() -> None:
    constraint = ToolSupport(tools=[WebSearch], custom_tools=False)
    value = [WebSearch(), {"type": "mcp", "server_label": "docs"}]
    assert constraint(value) is value

    for custom in ({"name": "lookup"}, {"type": "function"}):
        with pytest.raises(ConstraintViolationError, match="Custom tools"):
            constraint([custom])
