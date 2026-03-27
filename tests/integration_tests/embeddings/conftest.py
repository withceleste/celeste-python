"""Embeddings modality integration test fixtures."""

from pathlib import Path

import pytest

from celeste.artifacts import ImageArtifact, VideoArtifact
from celeste.mime_types import ImageMimeType, VideoMimeType

ASSETS_DIR = Path(__file__).parent.parent / "text" / "assets"


@pytest.fixture
def square_image() -> ImageArtifact:
    """Provide a square shape test image."""
    return ImageArtifact(
        path=str(ASSETS_DIR / "square.png"), mime_type=ImageMimeType.PNG
    )


@pytest.fixture
def test_video() -> VideoArtifact:
    """Provide a minimal test video (2s blue screen, 160x120)."""
    return VideoArtifact(
        path=str(ASSETS_DIR / "test_video.mp4"), mime_type=VideoMimeType.MP4
    )
