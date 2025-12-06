"""Simple test to verify Gradium STT is properly integrated in Celeste."""

import asyncio
from pathlib import Path

from celeste import Capability, Provider, create_client


async def test_simple_transcription():
    """Simple transcription test - the core functionality."""
    print("=" * 70)
    print("Testing Gradium STT integration in Celeste")
    print("=" * 70)

    # 1. Create client - should work out of the box
    print("\n1. Creating Gradium STT client...")
    client = create_client(
        capability=Capability.AUDIO_RECOGNITION,
        provider=Provider.GRADIUM,
        model="default",
    )
    print("   ✓ Client created successfully")

    # 2. Load audio file
    audio_path = Path("tests_maxence-gitignore/audio/audio_20251202_142441.wav")
    print(f"\n2. Loading audio file: {audio_path.name}")
    with open(audio_path, "rb") as f:
        audio_data = f.read()
    print(f"   ✓ Loaded {len(audio_data):,} bytes")

    # 3. Transcribe (the main use case)
    print("\n3. Transcribing audio...")
    result = await client.transcribe(audio_data, input_format="wav")
    print(f"   ✓ Transcription completed")

    # 4. Display results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"\nTranscription:\n  {result.content}\n")
    print(f"Characters: {result.usage.characters}")
    print(f"Duration: {result.usage.duration_s:.2f}s")
    print(f"Segments: {len(result.metadata.get('segments', []))}")

    print("\n" + "=" * 70)
    print("✅ Gradium STT is properly integrated in Celeste!")
    print("=" * 70)


async def test_streaming():
    """Test streaming functionality."""
    print("\n" + "=" * 70)
    print("Testing Gradium STT Streaming")
    print("=" * 70)

    client = create_client(
        capability=Capability.AUDIO_RECOGNITION,
        provider=Provider.GRADIUM,
        model="default",
    )

    # Simple async generator for audio chunks
    async def audio_chunks():
        audio_path = Path("tests_maxence-gitignore/audio/audio_20251202_142441.wav")
        with open(audio_path, "rb") as f:
            # Skip WAV header
            f.read(44)

            # Stream in chunks
            chunk_num = 0
            while True:
                chunk = f.read(3840)  # 1920 samples * 2 bytes
                if not chunk:
                    break
                chunk_num += 1
                yield chunk
                await asyncio.sleep(0)  # Allow other tasks

    print("\nStreaming audio chunks...")
    chunk_count = 0
    async for chunk in client.transcribe_stream(audio_chunks(), input_format="pcm"):
        chunk_count += 1
        print(f"  [{chunk.start_s:.2f}s] {chunk.content}")

    print(f"\n✓ Received {chunk_count} text chunks")

    print("\n" + "=" * 70)
    print("✅ Streaming works!")
    print("=" * 70)


async def main():
    """Run all tests."""
    try:
        # Test 1: Basic transcription (most important)
        await test_simple_transcription()

        # Test 2: Streaming (advanced feature)
        # await test_streaming()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
