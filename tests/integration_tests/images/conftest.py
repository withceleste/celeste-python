"""Images modality integration test fixtures."""

from pathlib import Path

import pytest

from celeste.artifacts import ImageArtifact
from celeste.mime_types import ImageMimeType

ASSETS_DIR = Path(__file__).parent / "assets"


@pytest.fixture
def square_image() -> ImageArtifact:
    """Provide a square shape test image."""
    return ImageArtifact(
        path=str(ASSETS_DIR / "square.png"), mime_type=ImageMimeType.PNG
    )
