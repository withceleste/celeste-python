"""Image header dimension parsing contracts."""

import struct

import pytest

from celeste.utils.image import get_image_dimensions


def _png(width: int, height: int, chunk: bytes = b"IHDR") -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n"
        + struct.pack(">I", 13)
        + chunk
        + struct.pack(">II", width, height)
        + b"\x08\x06\0\0\0\0\0\0\0"
    )


def _gif(signature: bytes, width: int, height: int) -> bytes:
    return signature + struct.pack("<HH", width, height) + b"\0" * 20


def _webp(kind: bytes, width: int, height: int) -> bytes:
    header = b"RIFF" + struct.pack("<I", 100) + b"WEBP" + kind
    if kind == b"VP8 ":
        return (
            header
            + struct.pack("<I", 50)
            + b"\0" * 6
            + struct.pack("<HH", width, height)
        )
    if kind == b"VP8X":
        return (
            header
            + struct.pack("<I", 10)
            + b"\0" * 4
            + struct.pack("<I", width - 1)[:3]
            + struct.pack("<I", height - 1)[:3]
        )
    w, h = width - 1, height - 1
    packed = bytes(
        [
            w & 0xFF,
            ((w >> 8) & 0x3F) | ((h & 0x03) << 6),
            (h >> 2) & 0xFF,
            (h >> 10) & 0x0F,
        ]
    )
    return header + struct.pack("<I", 10) + b"\x2f" + packed


def _jpeg(width: int, height: int, marker: bytes = b"\xff\xc0") -> bytes:
    return (
        b"\xff\xd8"
        + marker
        + struct.pack(">H", 11)
        + b"\x08"
        + struct.pack(">HH", height, width)
        + b"\x03"
        + b"\0" * 20
    )


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (_png(100, 200), (100, 200)),
        (_gif(b"GIF87a", 320, 240), (320, 240)),
        (_gif(b"GIF89a", 640, 480), (640, 480)),
        (_webp(b"VP8 ", 1280, 720), (1280, 720)),
        (_webp(b"VP8X", 1920, 1080), (1920, 1080)),
        (_webp(b"VP8L", 800, 600), (800, 600)),
        (_jpeg(1024, 768), (1024, 768)),
        (_jpeg(1920, 1080, b"\xff\xc2"), (1920, 1080)),
    ],
    ids=(
        "png",
        "gif87a",
        "gif89a",
        "webp-vp8",
        "webp-vp8x",
        "webp-vp8l",
        "jpeg",
        "jpeg-progressive",
    ),
)
def test_dimensions(data: bytes, expected: tuple[int, int]) -> None:
    assert get_image_dimensions(data) == expected


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"x" * 23,
        b"unknown format data here!!",
        _png(100, 200, b"XXXX"),
        b"RIFF" + struct.pack("<I", 100) + b"WEBPXXXX" + b"\0" * 20,
        b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\0" * 20,
        b"\xff\xd8\xff\xda" + b"\0" * 30,
    ],
    ids=(
        "empty",
        "short",
        "unknown",
        "png-no-ihdr",
        "webp-unknown",
        "jpeg-truncated",
        "jpeg-sos",
    ),
)
def test_invalid_or_truncated_data(data: bytes) -> None:
    assert get_image_dimensions(data) is None
