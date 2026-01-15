"""Minimal image dimension reader - pure Python, no dependencies.

Supports: PNG, JPEG, WebP (VP8/VP8L/VP8X), GIF.
Returns (width, height) or None if format unrecognized.
"""

import struct
from io import BytesIO


def get_image_dimensions(data: bytes) -> tuple[int, int] | None:
    """Get (width, height) from image bytes.

    Supports PNG, JPEG, WebP, GIF.
    Returns None if format is unrecognized or dimensions cannot be parsed.
    """
    if len(data) < 24:
        return None

    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return _get_png_dimensions(data)

    if data.startswith((b"GIF87a", b"GIF89a")):
        return _get_gif_dimensions(data)

    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return _get_webp_dimensions(data)

    if data.startswith(b"\xff\xd8"):
        return _get_jpeg_dimensions(data)

    return None


def _get_png_dimensions(data: bytes) -> tuple[int, int] | None:
    """Extract dimensions from PNG header (IHDR chunk)."""
    if data[12:16] != b"IHDR":
        return None
    try:
        w, h = struct.unpack(">II", data[16:24])
        return w, h
    except struct.error:
        return None


def _get_gif_dimensions(data: bytes) -> tuple[int, int] | None:
    """Extract dimensions from GIF header."""
    try:
        w, h = struct.unpack("<HH", data[6:10])
        return w, h
    except struct.error:
        return None


def _get_webp_dimensions(data: bytes) -> tuple[int, int] | None:
    """Extract dimensions from WebP header (VP8/VP8L/VP8X chunks)."""
    chunk_type = data[12:16]

    try:
        if chunk_type == b"VP8 ":  # Lossy
            if len(data) < 30:
                return None
            # RFC 6386: 14 bits width, 2 bits scale
            w, h = struct.unpack("<HH", data[26:30])
            return (w & 0x3FFF), (h & 0x3FFF)

        elif chunk_type == b"VP8X":  # Extended
            if len(data) < 30:
                return None
            # 24-bit width/height (stored as 3 bytes LE, 1-indexed)
            w = struct.unpack("<I", data[24:27] + b"\0")[0] + 1
            h = struct.unpack("<I", data[27:30] + b"\0")[0] + 1
            return w, h

        elif chunk_type == b"VP8L":  # Lossless
            if len(data) < 25:
                return None
            # 14 bits width/height packed in irregular bit layout
            b = data[21:25]
            w = 1 + (((b[1] & 0x3F) << 8) | b[0])
            h = 1 + (((b[3] & 0x0F) << 10) | (b[2] << 2) | ((b[1] & 0xC0) >> 6))
            return w, h

    except struct.error:
        return None

    return None


def _get_jpeg_dimensions(data: bytes) -> tuple[int, int] | None:
    """Extract dimensions from JPEG header (SOF marker)."""
    try:
        stream = BytesIO(data)
        stream.seek(2)

        while True:
            # Read marker
            b = stream.read(2)
            if len(b) < 2:
                break
            (marker,) = struct.unpack(">H", b)

            # SOS (Start of Scan) or EOI (End of Image) -> stop
            if marker == 0xFFDA or marker == 0xFFD9:
                break

            # Read chunk length
            b_len = stream.read(2)
            if len(b_len) < 2:
                break
            (size,) = struct.unpack(">H", b_len)

            # SOF markers (FFC0..FFCF) except DHT/JPG/DAC
            # SOF0=FFC0 (Baseline), SOF2=FFC2 (Progressive) are the common ones
            if 0xFFC0 <= marker <= 0xFFCF and marker not in (0xFFC4, 0xFFC8, 0xFFCC):
                stream.read(1)  # precision
                h, w = struct.unpack(">HH", stream.read(4))
                return w, h

            # Skip segment
            stream.seek(size - 2, 1)

    except (struct.error, ValueError):
        pass

    return None
