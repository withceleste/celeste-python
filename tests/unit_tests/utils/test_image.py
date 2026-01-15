"""Tests for celeste.utils.image module."""

import struct

from celeste.utils.image import get_image_dimensions


class TestGetImageDimensions:
    """Tests for get_image_dimensions function."""

    # --- PNG Tests ---

    def test_png_dimensions(self) -> None:
        """Test PNG dimension extraction."""
        # Minimal PNG header: signature + IHDR chunk with 100x200 dimensions
        width, height = 100, 200
        png_header = (
            b"\x89PNG\r\n\x1a\n"  # PNG signature (8 bytes)
            + struct.pack(">I", 13)  # IHDR chunk length (4 bytes)
            + b"IHDR"  # Chunk type (4 bytes)
            + struct.pack(">II", width, height)  # Width, Height (8 bytes)
            + b"\x08\x06\x00\x00\x00"  # Bit depth, color type, etc. (5 bytes)
            + b"\x00\x00\x00\x00"  # CRC placeholder (4 bytes)
        )
        assert get_image_dimensions(png_header) == (width, height)

    def test_png_large_dimensions(self) -> None:
        """Test PNG with large dimensions."""
        width, height = 4096, 2160
        png_header = (
            b"\x89PNG\r\n\x1a\n"
            + struct.pack(">I", 13)
            + b"IHDR"
            + struct.pack(">II", width, height)
            + b"\x08\x06\x00\x00\x00"
            + b"\x00\x00\x00\x00"
        )
        assert get_image_dimensions(png_header) == (width, height)

    def test_png_missing_ihdr(self) -> None:
        """Test PNG without IHDR chunk returns None."""
        png_header = (
            b"\x89PNG\r\n\x1a\n"
            + struct.pack(">I", 13)
            + b"XXXX"  # Wrong chunk type
            + struct.pack(">II", 100, 200)
            + b"\x08\x06\x00\x00\x00"
            + b"\x00\x00\x00\x00"
        )
        assert get_image_dimensions(png_header) is None

    # --- GIF Tests ---

    def test_gif87a_dimensions(self) -> None:
        """Test GIF87a dimension extraction."""
        width, height = 320, 240
        gif_header = b"GIF87a" + struct.pack("<HH", width, height) + b"\x00" * 20
        assert get_image_dimensions(gif_header) == (width, height)

    def test_gif89a_dimensions(self) -> None:
        """Test GIF89a dimension extraction."""
        width, height = 640, 480
        gif_header = b"GIF89a" + struct.pack("<HH", width, height) + b"\x00" * 20
        assert get_image_dimensions(gif_header) == (width, height)

    # --- WebP Tests ---

    def test_webp_vp8_lossy_dimensions(self) -> None:
        """Test WebP VP8 (lossy) dimension extraction."""
        width, height = 1280, 720
        # VP8 bitstream: dimensions at bytes 26-30 (14-bit values)
        webp_header = (
            b"RIFF"
            + struct.pack("<I", 100)  # File size
            + b"WEBP"
            + b"VP8 "  # Lossy chunk
            + struct.pack("<I", 50)  # Chunk size
            + b"\x00" * 6  # Padding to byte 26
            + struct.pack("<HH", width, height)  # Dimensions
            + b"\x00" * 20  # More padding
        )
        assert get_image_dimensions(webp_header) == (width, height)

    def test_webp_vp8x_extended_dimensions(self) -> None:
        """Test WebP VP8X (extended) dimension extraction."""
        width, height = 1920, 1080
        # VP8X: 24-bit LE width/height at bytes 24-29, stored as value-1
        webp_header = (
            b"RIFF"
            + struct.pack("<I", 100)  # File size
            + b"WEBP"
            + b"VP8X"  # Extended chunk
            + struct.pack("<I", 10)  # Chunk size
            + b"\x00" * 4  # Flags
            # Canvas width-1 (3 bytes LE) at offset 24
            + struct.pack("<I", width - 1)[:3]
            # Canvas height-1 (3 bytes LE) at offset 27
            + struct.pack("<I", height - 1)[:3]
            + b"\x00" * 20
        )
        assert get_image_dimensions(webp_header) == (width, height)

    def test_webp_vp8l_lossless_dimensions(self) -> None:
        """Test WebP VP8L (lossless) dimension extraction."""
        width, height = 800, 600
        # VP8L: signature byte + packed 14-bit dimensions
        # Bits 0-13: width-1, Bits 14-27: height-1
        w_minus_1 = width - 1
        h_minus_1 = height - 1
        # Pack into 4 bytes with irregular bit layout
        b0 = w_minus_1 & 0xFF
        b1 = ((w_minus_1 >> 8) & 0x3F) | ((h_minus_1 & 0x03) << 6)
        b2 = (h_minus_1 >> 2) & 0xFF
        b3 = (h_minus_1 >> 10) & 0x0F
        packed = bytes([b0, b1, b2, b3])

        webp_header = (
            b"RIFF"
            + struct.pack("<I", 100)  # File size
            + b"WEBP"
            + b"VP8L"  # Lossless chunk
            + struct.pack("<I", 10)  # Chunk size
            + b"\x2f"  # VP8L signature byte
            + packed  # Packed dimensions at bytes 21-24
            + b"\x00" * 20
        )
        assert get_image_dimensions(webp_header) == (width, height)

    def test_webp_unknown_chunk(self) -> None:
        """Test WebP with unknown chunk type returns None."""
        webp_header = (
            b"RIFF"
            + struct.pack("<I", 100)
            + b"WEBP"
            + b"XXXX"  # Unknown chunk
            + b"\x00" * 30
        )
        assert get_image_dimensions(webp_header) is None

    # --- JPEG Tests ---

    def test_jpeg_baseline_dimensions(self) -> None:
        """Test JPEG baseline (SOF0) dimension extraction."""
        width, height = 1024, 768
        # JPEG: SOI + APP0 + SOF0 with dimensions
        jpeg_header = (
            b"\xff\xd8"  # SOI marker
            + b"\xff\xe0"  # APP0 marker
            + struct.pack(">H", 16)  # APP0 length
            + b"JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"  # APP0 data
            + b"\xff\xc0"  # SOF0 marker (baseline)
            + struct.pack(">H", 11)  # SOF0 length
            + b"\x08"  # Precision
            + struct.pack(">HH", height, width)  # Height, Width (JPEG order)
            + b"\x03"  # Components
            + b"\x00" * 20
        )
        assert get_image_dimensions(jpeg_header) == (width, height)

    def test_jpeg_progressive_dimensions(self) -> None:
        """Test JPEG progressive (SOF2) dimension extraction."""
        width, height = 1920, 1080
        jpeg_header = (
            b"\xff\xd8"  # SOI marker
            + b"\xff\xc2"  # SOF2 marker (progressive)
            + struct.pack(">H", 11)  # SOF2 length
            + b"\x08"  # Precision
            + struct.pack(">HH", height, width)  # Height, Width
            + b"\x03"
            + b"\x00" * 20
        )
        assert get_image_dimensions(jpeg_header) == (width, height)

    def test_jpeg_with_dht_before_sof(self) -> None:
        """Test JPEG with DHT marker before SOF (should skip DHT)."""
        width, height = 640, 480
        jpeg_header = (
            b"\xff\xd8"  # SOI
            + b"\xff\xc4"  # DHT marker (should be skipped)
            + struct.pack(">H", 10)  # DHT length
            + b"\x00" * 8  # DHT data
            + b"\xff\xc0"  # SOF0
            + struct.pack(">H", 11)
            + b"\x08"
            + struct.pack(">HH", height, width)
            + b"\x03"
            + b"\x00" * 20
        )
        assert get_image_dimensions(jpeg_header) == (width, height)

    # --- Edge Cases ---

    def test_empty_data(self) -> None:
        """Test empty data returns None."""
        assert get_image_dimensions(b"") is None

    def test_too_short_data(self) -> None:
        """Test data shorter than 24 bytes returns None."""
        assert get_image_dimensions(b"\x89PNG\r\n\x1a\n") is None
        assert get_image_dimensions(b"x" * 23) is None

    def test_unknown_format(self) -> None:
        """Test unknown format returns None."""
        assert get_image_dimensions(b"unknown format data here!!") is None

    def test_garbage_data(self) -> None:
        """Test random garbage returns None."""
        import os

        garbage = os.urandom(100)
        # Should not raise, just return None
        result = get_image_dimensions(garbage)
        assert result is None or isinstance(result, tuple)

    def test_truncated_jpeg(self) -> None:
        """Test truncated JPEG returns None."""
        # JPEG header that starts scanning but runs out of data
        truncated = b"\xff\xd8\xff\xe0\x00\x10" + b"JFIF" + b"\x00" * 20
        assert get_image_dimensions(truncated) is None

    def test_jpeg_with_sos_before_sof(self) -> None:
        """Test JPEG with SOS marker before SOF returns None."""
        # Malformed JPEG with SOS before SOF
        jpeg_header = (
            b"\xff\xd8"  # SOI
            + b"\xff\xda"  # SOS marker (stops scanning)
            + b"\x00" * 30
        )
        assert get_image_dimensions(jpeg_header) is None
