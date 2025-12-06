"""Test Gradium STT Streaming functionality."""

import asyncio
import logging
from pathlib import Path

from celeste import Capability, Provider, create_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def audio_file_generator(file_path: Path, chunk_size: int = 3840, skip_header: bool = True):
    """Generate audio chunks from a file.

    Args:
        file_path: Path to audio file
        chunk_size: Bytes per chunk (default 3840 = 1920 samples * 2 bytes for 24kHz PCM)
        skip_header: Skip WAV header to get raw PCM

    Yields:
        bytes: Audio chunks
    """
    with open(file_path, "rb") as f:
        # Skip WAV header if requested (44 bytes)
        if skip_header and file_path.suffix.lower() == ".wav":
            f.read(44)

        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk
            # Small delay to simulate real-time streaming
            await asyncio.sleep(0.08)  # 80ms chunks


async def test_streaming_transcription():
    """Test real-time streaming transcription."""
    print("\n" + "=" * 70)
    print("🎤 GRADIUM STT STREAMING TEST")
    print("=" * 70)

    client = create_client(
        capability=Capability.AUDIO_RECOGNITION,
        provider=Provider.GRADIUM,
        model="default",
    )

    audio_path = Path("tests_maxence-gitignore/audio/audio_20251202_142441.wav")
    print(f"\n[Test] Streaming audio file: {audio_path}")
    print(f"  File size: {audio_path.stat().st_size:,} bytes")
    print(f"  Format: PCM (extracted from WAV)")

    # Create audio stream - skip WAV header to stream raw PCM
    audio_stream = audio_file_generator(audio_path, chunk_size=3840, skip_header=True)

    print("\n[Streaming] Starting real-time transcription...")
    print("-" * 70)

    chunk_count = 0
    full_transcription = []

    try:
        async for chunk in client.transcribe_stream(audio_stream, input_format="pcm"):
            chunk_count += 1
            full_transcription.append(chunk.content)

            # Display chunk in real-time
            start_time = f"{chunk.start_s:.2f}s" if chunk.start_s is not None else "?.??s"
            stop_time = f"{chunk.stop_s:.2f}s" if chunk.stop_s is not None else "?"

            print(f"[{start_time:>6}] {chunk.content}")

    except Exception as e:
        print(f"\n❌ Streaming error: {e}")
        raise

    print("-" * 70)
    print("\n✓ Streaming completed!")
    print(f"\n  Total chunks received: {chunk_count}")
    print(f"  Full transcription: {' '.join(full_transcription)}")
    print(f"  Total characters: {sum(len(text) for text in full_transcription)}")

    print("\n" + "=" * 70)
    print("✅ STREAMING TEST PASSED!")
    print("=" * 70)


async def test_pcm_streaming():
    """Test streaming with raw PCM audio."""
    print("\n" + "=" * 70)
    print("🎤 GRADIUM STT - PCM STREAMING TEST")
    print("=" * 70)

    client = create_client(
        capability=Capability.AUDIO_RECOGNITION,
        provider=Provider.GRADIUM,
        model="default",
    )

    # Load WAV and skip header to get raw PCM
    audio_path = Path("tests_maxence-gitignore/audio/audio_20251202_142441.wav")
    print(f"\n[Test] Streaming PCM audio from: {audio_path}")

    async def pcm_generator():
        """Generate raw PCM chunks."""
        with open(audio_path, "rb") as f:
            # Skip 44-byte WAV header
            f.read(44)

            while True:
                # Read 1920 samples * 2 bytes = 3840 bytes (80ms at 24kHz)
                chunk = f.read(3840)
                if not chunk:
                    break
                yield chunk
                await asyncio.sleep(0.05)  # Simulate real-time

    print("\n[Streaming] Transcribing PCM audio...")

    chunk_count = 0
    async for chunk in client.transcribe_stream(pcm_generator(), input_format="pcm"):
        chunk_count += 1
        if chunk_count <= 10:  # Show first 10 chunks
            print(f"  [{chunk.start_s:.2f}s] {chunk.content}")

    print(f"\n✓ Received {chunk_count} chunks via PCM streaming")

    print("\n" + "=" * 70)
    print("✅ PCM STREAMING TEST PASSED!")
    print("=" * 70)


async def main():
    """Run all streaming tests."""
    print("\n" + "=" * 70)
    print("🎤 GRADIUM STT - STREAMING TEST SUITE")
    print("=" * 70)

    try:
        # Test 1: WAV streaming
        await test_streaming_transcription()

        # Test 2: PCM streaming
        await test_pcm_streaming()

        print("\n" + "=" * 70)
        print("✅ ALL STREAMING TESTS PASSED!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ ERROR OCCURRED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
