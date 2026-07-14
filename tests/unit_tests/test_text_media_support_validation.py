"""Text media support follows model constraints."""

import pytest
from pydantic import SecretStr

from celeste.artifacts import (
    AudioArtifact,
    DocumentArtifact,
    ImageArtifact,
    VideoArtifact,
)
from celeste.auth import AuthHeader
from celeste.constraints import (
    AudioConstraint,
    Constraint,
    DocumentsConstraint,
    ImagesConstraint,
    VideosConstraint,
)
from celeste.core import InputType, Modality, Operation, Provider
from celeste.modalities.text.parameters import TextParameter
from celeste.modalities.text.providers.google.client import GoogleTextClient
from celeste.models import Model
from celeste.types import ImagePart, Message, Role, TextPart

type MediaArtifact = AudioArtifact | DocumentArtifact | ImageArtifact | VideoArtifact


def _client(
    parameter: TextParameter | None = None,
    constraint: Constraint | None = None,
) -> GoogleTextClient:
    constraints = (
        {parameter: constraint}
        if parameter is not None and constraint is not None
        else {}
    )
    model = Model(
        id="test",
        provider=Provider.GOOGLE,
        display_name="test",
        operations={Modality.TEXT: {Operation.ANALYZE}},
        parameter_constraints=constraints,
    )
    return GoogleTextClient(
        model=model,
        provider=Provider.GOOGLE,
        auth=AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix=""),
    )


MEDIA_CASES = [
    (
        TextParameter.IMAGE,
        ImagesConstraint(),
        InputType.IMAGE,
        "image",
        ImageArtifact(data=b"x"),
    ),
    (
        TextParameter.VIDEO,
        VideosConstraint(),
        InputType.VIDEO,
        "video",
        VideoArtifact(data=b"x"),
    ),
    (
        TextParameter.AUDIO,
        AudioConstraint(),
        InputType.AUDIO,
        "audio",
        AudioArtifact(data=b"x"),
    ),
    (
        TextParameter.DOCUMENT,
        DocumentsConstraint(),
        InputType.DOCUMENT,
        "document",
        DocumentArtifact(data=b"x"),
    ),
]


@pytest.mark.parametrize(
    ("parameter", "constraint", "input_type", "argument", "artifact"), MEDIA_CASES
)
def test_declared_media_is_allowed(
    parameter: TextParameter,
    constraint: Constraint,
    input_type: InputType,
    argument: str,
    artifact: MediaArtifact,
) -> None:
    client = _client(parameter, constraint)
    assert client.model.optional_input_types == {input_type}
    client._check_media_support(**{argument: artifact})


@pytest.mark.parametrize(
    ("_parameter", "_constraint", "input_type", "argument", "artifact"), MEDIA_CASES
)
def test_undeclared_media_is_rejected(
    _parameter: TextParameter,
    _constraint: Constraint,
    input_type: InputType,
    argument: str,
    artifact: MediaArtifact,
) -> None:
    with pytest.raises(
        NotImplementedError, match=f"does not support {input_type.value}"
    ):
        _client()._check_media_support(**{argument: artifact})


@pytest.mark.parametrize("supported", [False, True])
def test_message_media_uses_same_validation(supported: bool) -> None:
    client = (
        _client(TextParameter.IMAGE, ImagesConstraint()) if supported else _client()
    )
    message = Message(
        role=Role.USER,
        content=[TextPart(text="look"), ImagePart(image=ImageArtifact(data=b"x"))],
    )
    if supported:
        client._check_media_support(messages=[message])
    else:
        with pytest.raises(NotImplementedError, match="does not support image"):
            client._check_media_support(messages=[message])
