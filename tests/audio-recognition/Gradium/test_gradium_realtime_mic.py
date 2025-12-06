"""Test Gradium STT with real-time microphone input."""

import asyncio
import logging
from collections.abc import AsyncGenerator

try:
    import pyaudio
except ImportError:
    print("❌ pyaudio not installed!")
    print("Install with: pip install pyaudio")
    print("On macOS: brew install portaudio && pip install pyaudio")
    exit(1)

import websockets

from celeste import Capability, Provider, create_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)

# Audio configuration for Gradium STT
SAMPLE_RATE = 24000  # Hz
CHUNK_SIZE = 1920  # samples per chunk (80ms at 24kHz)
CHANNELS = 1  # mono
FORMAT = pyaudio.paInt16  # 16-bit PCM


async def microphone_stream(show_header: bool = True) -> AsyncGenerator[bytes, None]:
    """Stream audio from microphone.

    Args:
        show_header: Show microphone info header

    Yields:
        bytes: Audio chunks from microphone
    """
    audio = pyaudio.PyAudio()

    try:
        # Open microphone stream
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
        )

        if show_header:
            print(f"\n🎤 Microphone opened:")
            print(f"  Sample rate: {SAMPLE_RATE} Hz")
            print(f"  Channels: {CHANNELS} (mono)")
            print(f"  Chunk size: {CHUNK_SIZE} samples ({CHUNK_SIZE / SAMPLE_RATE * 1000:.0f}ms)")
            print(f"  Format: 16-bit PCM")
            print("\n🔴 Recording... (Press Ctrl+C to stop)\n")

        try:
            while True:
                # Read audio chunk from microphone
                audio_chunk = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                yield audio_chunk
                await asyncio.sleep(0)  # Allow other tasks to run

        except KeyboardInterrupt:
            print("\n\n⏹️  Recording stopped by user")

        finally:
            stream.stop_stream()
            stream.close()

    finally:
        audio.terminate()


async def test_realtime_microphone():
    """Test real-time microphone transcription with auto-reconnect."""
    print("=" * 70)
    print("🎤 GRADIUM STT - REAL-TIME MICROPHONE TEST")
    print("=" * 70)
    print("\nThis test will:")
    print("  1. Open your microphone")
    print("  2. Stream audio to Gradium STT in real-time")
    print("  3. Display transcription as you speak")
    print("  4. Auto-reconnect after pauses")
    print("\nPress Ctrl+C to stop recording\n")

    input("Press ENTER to start recording... ")

    client = create_client(
        capability=Capability.AUDIO_RECOGNITION,
        provider=Provider.GRADIUM,
        model="default",
    )

    print("\n" + "=" * 70)
    print("📝 TRANSCRIPTION (real-time)")
    print("=" * 70 + "\n")

    session_count = 0

    try:
        while True:
            session_count += 1
            if session_count > 1:
                print(f"\n🔄 Session {session_count} - Ready for more speech...")

            try:
                mic_stream = microphone_stream(show_header=(session_count == 1))

                async for chunk in client.transcribe_stream(mic_stream, input_format="pcm"):
                    # Display transcription in real-time
                    timestamp = f"[{chunk.start_s:.1f}s]" if chunk.start_s else "[?.?s]"
                    print(f"{timestamp:>8} {chunk.content}", flush=True)

            except websockets.exceptions.ConnectionClosed:
                # Connection closed (probably due to inactivity/VAD)
                print("\n⏸️  Pause detected - waiting for speech...")
                await asyncio.sleep(1)
                continue  # Reconnect

            except Exception as e:
                if "end_of_stream" in str(e).lower():
                    print("\n⏸️  Stream ended - restarting...")
                    await asyncio.sleep(0.5)
                    continue
                else:
                    raise

    except KeyboardInterrupt:
        print("\n\n✓ Test stopped by user")
        print(f"  Total sessions: {session_count}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
    print("✅ REAL-TIME MICROPHONE TEST COMPLETED")
    print("=" * 70)


async def test_with_vad():
    """Test with voice activity detection to stop automatically."""
    print("=" * 70)
    print("🎤 GRADIUM STT - MICROPHONE WITH VAD")
    print("=" * 70)
    print("\nThis test will automatically stop when you stop speaking\n")

    input("Press ENTER to start recording... ")

    client = create_client(
        capability=Capability.AUDIO_RECOGNITION,
        provider=Provider.GRADIUM,
        model="default",
    )

    print("\n📝 Speak now... (will auto-stop on silence)\n")

    # TODO: Implement VAD-based auto-stop
    # For now, just use the basic test
    print("⚠️  VAD auto-stop not yet implemented - use Ctrl+C")
    await test_realtime_microphone()


async def main():
    """Run real-time microphone tests."""
    try:
        await test_realtime_microphone()

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✓ Exited")
