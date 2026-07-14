from typing import cast

import pytest

from celeste.artifacts import (
    AudioArtifact,
    DocumentArtifact,
    ImageArtifact,
    VideoArtifact,
)
from celeste.constraints import (
    AudioConstraint,
    Bool,
    DocumentsConstraint,
    ImageConstraint,
    Str,
    VideosConstraint,
)
from celeste.core import InputType
from celeste.io import _extract_input_type, get_constraint_input_type


@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        (str, InputType.TEXT),
        (ImageArtifact, InputType.IMAGE),
        (list[VideoArtifact], InputType.VIDEO),
        (cast(type, AudioArtifact | None), InputType.AUDIO),
        (DocumentArtifact, InputType.DOCUMENT),
        (int, None),
    ],
)
def test_extract_input_type(annotation: type, expected: InputType | None) -> None:
    assert _extract_input_type(annotation) == expected


@pytest.mark.parametrize(
    ("constraint", "expected"),
    [
        (ImageConstraint(), InputType.IMAGE),
        (VideosConstraint(), InputType.VIDEO),
        (AudioConstraint(), InputType.AUDIO),
        (DocumentsConstraint(), InputType.DOCUMENT),
        (Str(), InputType.TEXT),
        (Bool(), None),
    ],
)
def test_constraint_input_type(constraint: object, expected: InputType | None) -> None:
    assert get_constraint_input_type(constraint) == expected  # type: ignore[arg-type]
