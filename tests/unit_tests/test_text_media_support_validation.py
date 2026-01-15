"""Unit tests for TextClient media support validation."""

import pytest
from pydantic import SecretStr

from celeste import Model
from celeste.artifacts import ImageArtifact, VideoArtifact
from celeste.auth import AuthHeader
from celeste.constraints import ImagesConstraint, VideosConstraint
from celeste.core import InputType, Modality, Operation, Provider
from celeste.modalities.text.parameters import TextParameter
from celeste.modalities.text.providers.google.client import GoogleTextClient


@pytest.fixture
def model_with_image_support() -> Model:
    """Model that declares image support."""
    return Model(
        id="test-vision",
        provider=Provider.GOOGLE,
        display_name="Test Vision",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            TextParameter.IMAGE: ImagesConstraint(),
        },
    )


@pytest.fixture
def model_with_video_support() -> Model:
    """Model that declares video support."""
    return Model(
        id="test-video",
        provider=Provider.GOOGLE,
        display_name="Test Video",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            TextParameter.VIDEO: VideosConstraint(),
        },
    )


@pytest.fixture
def model_without_media_support() -> Model:
    """Model that declares no media support."""
    return Model(
        id="test-text-only",
        provider=Provider.GOOGLE,
        display_name="Test Text Only",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={},
    )


@pytest.fixture
def google_auth() -> AuthHeader:
    """Google auth header."""
    return AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix="")


def test_model_optional_input_types_computed_from_constraints(
    model_with_image_support: Model,
    model_with_video_support: Model,
    model_without_media_support: Model,
) -> None:
    """Verify optional_input_types is correctly computed from parameter_constraints."""
    assert InputType.IMAGE in model_with_image_support.optional_input_types
    assert InputType.VIDEO not in model_with_image_support.optional_input_types

    assert InputType.VIDEO in model_with_video_support.optional_input_types
    assert InputType.IMAGE not in model_with_video_support.optional_input_types

    assert InputType.IMAGE not in model_without_media_support.optional_input_types
    assert InputType.VIDEO not in model_without_media_support.optional_input_types


def test_check_media_support_allows_image_when_declared(
    model_with_image_support: Model,
    google_auth: AuthHeader,
) -> None:
    """Image input should be allowed when model declares ImagesConstraint."""
    client = GoogleTextClient(
        model=model_with_image_support,
        provider=Provider.GOOGLE,
        auth=google_auth,
    )

    # Should not raise
    client._check_media_support(
        image=ImageArtifact(data=b"test"),
        video=None,
        audio=None,
    )


def test_check_media_support_allows_video_when_declared(
    model_with_video_support: Model,
    google_auth: AuthHeader,
) -> None:
    """Video input should be allowed when model declares VideosConstraint."""
    client = GoogleTextClient(
        model=model_with_video_support,
        provider=Provider.GOOGLE,
        auth=google_auth,
    )

    # Should not raise
    client._check_media_support(
        image=None,
        video=VideoArtifact(data=b"test"),
        audio=None,
    )


def test_check_media_support_rejects_image_when_not_declared(
    model_without_media_support: Model,
    google_auth: AuthHeader,
) -> None:
    """Image input should raise NotImplementedError when model doesn't declare support."""
    client = GoogleTextClient(
        model=model_without_media_support,
        provider=Provider.GOOGLE,
        auth=google_auth,
    )

    with pytest.raises(NotImplementedError, match="does not support image input"):
        client._check_media_support(
            image=ImageArtifact(data=b"test"),
            video=None,
            audio=None,
        )


def test_check_media_support_rejects_video_when_not_declared(
    model_without_media_support: Model,
    google_auth: AuthHeader,
) -> None:
    """Video input should raise NotImplementedError when model doesn't declare support."""
    client = GoogleTextClient(
        model=model_without_media_support,
        provider=Provider.GOOGLE,
        auth=google_auth,
    )

    with pytest.raises(NotImplementedError, match="does not support video input"):
        client._check_media_support(
            image=None,
            video=VideoArtifact(data=b"test"),
            audio=None,
        )


def test_check_media_support_rejects_video_on_image_only_model(
    model_with_image_support: Model,
    google_auth: AuthHeader,
) -> None:
    """Video should be rejected on model that only declares image support."""
    client = GoogleTextClient(
        model=model_with_image_support,
        provider=Provider.GOOGLE,
        auth=google_auth,
    )

    with pytest.raises(NotImplementedError, match="does not support video input"):
        client._check_media_support(
            image=None,
            video=VideoArtifact(data=b"test"),
            audio=None,
        )


def test_check_media_support_allows_none_values(
    model_without_media_support: Model,
    google_auth: AuthHeader,
) -> None:
    """None values should always be allowed (no media provided)."""
    client = GoogleTextClient(
        model=model_without_media_support,
        provider=Provider.GOOGLE,
        auth=google_auth,
    )

    # Should not raise - no media provided
    client._check_media_support(image=None, video=None, audio=None)
