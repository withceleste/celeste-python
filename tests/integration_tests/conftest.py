from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio

from celeste.artifacts import (
    AudioArtifact,
    DocumentArtifact,
    ImageArtifact,
    VideoArtifact,
)
from celeste.http import close_all_http_clients
from celeste.mime_types import (
    AudioMimeType,
    DocumentMimeType,
    ImageMimeType,
    VideoMimeType,
)

ASSETS = Path(__file__).parent / "text" / "assets"


@pytest_asyncio.fixture(autouse=True)
async def cleanup_http_clients() -> AsyncGenerator[None, None]:
    yield
    await close_all_http_clients()


@pytest.fixture(scope="session")
def square_image() -> ImageArtifact:
    return ImageArtifact(path=str(ASSETS / "square.png"), mime_type=ImageMimeType.PNG)


@pytest.fixture(scope="session")
def test_audio() -> AudioArtifact:
    return AudioArtifact(
        path=str(ASSETS / "test_audio.mp3"), mime_type=AudioMimeType.MP3
    )


@pytest.fixture(scope="session")
def test_document() -> DocumentArtifact:
    return DocumentArtifact(
        path=str(ASSETS / "test_document.pdf"), mime_type=DocumentMimeType.PDF
    )


@pytest.fixture(scope="session")
def test_video() -> VideoArtifact:
    return VideoArtifact(
        path=str(ASSETS / "test_video.mp4"), mime_type=VideoMimeType.MP4
    )
