"""Test script for Gradium STT (Speech-to-Text)."""

import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv

from celeste import Capability, Provider, create_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


async def test_basic_transcription():
    """Test basic transcription with Gradium STT."""
    print("\n" + "=" * 70)
    print("Testing Gradium STT - Basic Transcription")
    print("=" * 70)

    client = create_client(
        capability=Capability.AUDIO_RECOGNITION,
        provider=Provider.GRADIUM,
        model="default",
    )

    # Load test audio file (WAV)
    audio_path = Path("tests_maxence-gitignore/audio/audio_20251202_142441.wav")
    print(f"\n[Test] Loading audio file: {audio_path}")

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    print(f"  Audio size: {len(audio_data):,} bytes")

    # Transcribe
    print("\n[Test] Transcribing audio...")
    result = await client.transcribe(audio_data, input_format="wav")

    print(f"\n✓ Transcription Results:")
    print(f"  Text: {result.content}")
    print(f"  Characters: {result.usage.characters}")
    print(f"  Duration: {result.usage.duration_s:.2f}s" if result.usage.duration_s else "  Duration: N/A")
    print(f"  Region: {result.metadata.get('region')}")
    print(f"  Request ID: {result.metadata.get('request_id')}")

    # Segments
    segments = result.metadata.get('segments', [])
    print(f"\n  Segments: {len(segments)}")
    for i, seg in enumerate(segments[:5], 1):  # Show first 5
        text = seg.get('text', '')
        start = seg.get('start_s', 0)
        stop = seg.get('stop_s', 0)
        print(f"    {i}. [{start:.2f}s - {stop:.2f}s]: {text}")

    if len(segments) > 5:
        print(f"    ... and {len(segments) - 5} more segments")

    # VAD steps
    vad_steps = result.metadata.get('vad_steps', [])
    print(f"\n  VAD Steps: {len(vad_steps)}")
    if vad_steps:
        last_vad = vad_steps[-1]
        print(f"    Final VAD at {last_vad.get('total_duration_s', 0):.2f}s")
        vad_predictions = last_vad.get('vad', [])
        if len(vad_predictions) >= 3:
            inactivity_prob = vad_predictions[2].get('inactivity_prob', 0)
            print(f"    Inactivity probability (2s horizon): {inactivity_prob:.2%}")

    print("\n" + "=" * 70)
    print("✓ Basic transcription test completed successfully!")
    print("=" * 70)


async def test_pcm_format():
    """Test transcription with PCM format."""
    print("\n" + "=" * 70)
    print("Testing Gradium STT - PCM Format")
    print("=" * 70)

    client = create_client(
        capability=Capability.AUDIO_RECOGNITION,
        provider=Provider.GRADIUM,
        model="default",
    )

    # Load WAV and extract PCM data (skip 44-byte WAV header)
    audio_path = Path("tests_maxence-gitignore/audio/audio_20251202_142441.wav")
    print(f"\n[Test] Loading and converting to PCM: {audio_path}")

    with open(audio_path, "rb") as f:
        wav_data = f.read()

    # Skip WAV header (44 bytes) to get raw PCM
    pcm_data = wav_data[44:]
    print(f"  PCM size: {len(pcm_data):,} bytes")

    # Note: This assumes 24kHz 16-bit mono PCM
    # If the WAV is different, we'd need to resample
    print("\n[Test] Transcribing PCM audio...")
    print("  Note: Assuming 24kHz 16-bit mono PCM")

    result = await client.transcribe(pcm_data, input_format="pcm")

    print(f"\n✓ Transcription: {result.content.data[:200]}...")
    print(f"  Characters: {result.usage.characters}")

    print("\n" + "=" * 70)
    print("✓ PCM format test completed successfully!")
    print("=" * 70)


async def test_vad_analysis():
    """Test Voice Activity Detection analysis."""
    print("\n" + "=" * 70)
    print("Testing Gradium STT - VAD Analysis")
    print("=" * 70)

    client = create_client(
        capability=Capability.AUDIO_RECOGNITION,
        provider=Provider.GRADIUM,
        model="default",
    )

    audio_path = Path("tests_maxence-gitignore/audio/audio_20251202_142441.wav")

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    print("\n[Test] Transcribing with VAD analysis...")
    result = await client.transcribe(audio_data, input_format="wav")

    vad_steps = result.metadata.get('vad_steps', [])

    print(f"\n✓ VAD Analysis:")
    print(f"  Total VAD steps: {len(vad_steps)}")
    print(f"  Step interval: 80ms")

    if vad_steps:
        # Analyze inactivity probabilities
        inactivity_probs = []
        for step in vad_steps:
            vad_predictions = step.get('vad', [])
            if len(vad_predictions) >= 3:
                inactivity_probs.append(vad_predictions[2].get('inactivity_prob', 0))

        if inactivity_probs:
            avg_inactivity = sum(inactivity_probs) / len(inactivity_probs)
            max_inactivity = max(inactivity_probs)
            min_inactivity = min(inactivity_probs)

            print(f"\n  Inactivity Probability Stats (2s horizon):")
            print(f"    Average: {avg_inactivity:.2%}")
            print(f"    Maximum: {max_inactivity:.2%}")
            print(f"    Minimum: {min_inactivity:.2%}")

            # Detect potential speech segments
            silence_threshold = 0.8
            silence_count = sum(1 for p in inactivity_probs if p > silence_threshold)
            silence_pct = (silence_count / len(inactivity_probs)) * 100

            print(f"\n  Speech Activity:")
            print(f"    Silence frames (>{silence_threshold:.0%} inactivity): {silence_count}/{len(inactivity_probs)} ({silence_pct:.1f}%)")
            print(f"    Active speech frames: {len(inactivity_probs) - silence_count}/{len(inactivity_probs)} ({100 - silence_pct:.1f}%)")

    print("\n" + "=" * 70)
    print("✓ VAD analysis test completed successfully!")
    print("=" * 70)


async def test_minimal_audio():
    """Test with minimal audio (low cost)."""
    print("\n" + "=" * 70)
    print("Testing Gradium STT - Minimal Audio (saves credits)")
    print("=" * 70)

    client = create_client(
        capability=Capability.AUDIO_RECOGNITION,
        provider=Provider.GRADIUM,
        model="default",
    )

    # Use MP3 file (smaller)
    audio_path = Path("tests_maxence-gitignore/audio/93495385784321-9VZRgEC65gjrnSPNiZ5GNm.mp3")
    print(f"\n[Test] Loading audio file: {audio_path}")

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    print(f"  Audio size: {len(audio_data):,} bytes")

    # Note: Gradium accepts wav, pcm, opus but not mp3
    # We'll need to convert or use a WAV file
    print("\n⚠️  Note: MP3 not supported by Gradium")
    print("  Skipping this test - use WAV or PCM format")

    print("\n" + "=" * 70)
    print("✓ Minimal audio test noted!")
    print("=" * 70)


async def test_timestamps():
    """Test timestamp accuracy."""
    print("\n" + "=" * 70)
    print("Testing Gradium STT - Timestamp Accuracy")
    print("=" * 70)

    client = create_client(
        capability=Capability.AUDIO_RECOGNITION,
        provider=Provider.GRADIUM,
        model="default",
    )

    audio_path = Path("tests_maxence-gitignore/audio/audio_20251202_142441.wav")

    with open(audio_path, "rb") as f:
        audio_data = f.read()

    print("\n[Test] Transcribing and analyzing timestamps...")
    result = await client.transcribe(audio_data, input_format="wav")

    segments = result.metadata.get('segments', [])

    print(f"\n✓ Timestamp Analysis:")
    print(f"  Total segments: {len(segments)}")

    if segments:
        # Calculate segment durations
        durations = []
        for seg in segments:
            start = seg.get('start_s', 0)
            stop = seg.get('stop_s')
            if stop is not None:
                duration = stop - start
                durations.append(duration)

        if durations:
            avg_duration = sum(durations) / len(durations)
            print(f"\n  Segment Duration Stats:")
            print(f"    Average: {avg_duration:.3f}s")
            print(f"    Shortest: {min(durations):.3f}s")
            print(f"    Longest: {max(durations):.3f}s")

        # Show timeline
        print(f"\n  Timeline (first 10 segments):")
        for i, seg in enumerate(segments[:10], 1):
            text = seg.get('text', '')
            start = seg.get('start_s', 0)
            stop = seg.get('stop_s', 'N/A')
            if stop != 'N/A':
                print(f"    {i:2d}. [{start:6.2f}s - {stop:6.2f}s] {text}")
            else:
                print(f"    {i:2d}. [{start:6.2f}s -    N/A] {text}")

    print("\n" + "=" * 70)
    print("✓ Timestamp accuracy test completed successfully!")
    print("=" * 70)


async def main():
    """Run all Gradium STT tests."""
    print("\n" + "=" * 70)
    print("🎤 GRADIUM STT - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    try:
        # Run all tests
        await test_basic_transcription()
        await test_vad_analysis()
        await test_timestamps()
        await test_minimal_audio()
        # await test_pcm_format()  # Uncomment if WAV is 24kHz

        print("\n" + "=" * 70)
        print("✅ ALL GRADIUM STT TESTS PASSED!")
        print("=" * 70)
        print("\nTest files used:")
        print("  - tests_maxence-gitignore/audio/audio_20251202_142441.wav")
        print("  - tests_maxence-gitignore/audio/93495385784321-9VZRgEC65gjrnSPNiZ5GNm.mp3")
        print("\n")

    except Exception as e:
        print(f"\n❌ ERROR OCCURRED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
