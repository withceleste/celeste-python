# Gradium Audio Recognition Provider

High-performance Speech-to-Text with real-time streaming support.

## Overview

Gradium provides low-latency STT transcription with advanced features:
- ⚡ **Low Latency**: <300ms time-to-first-token
- 🌐 **WebSocket Streaming**: Real-time bidirectional communication
- 🔊 **Voice Activity Detection**: Built-in speech/silence detection
- 🌍 **Multi-language**: Auto-detect multiple languages
- 📍 **Timestamps**: Precise word-level timing

## Quick Start

### Basic Transcription

```python
from celeste import create_client, Capability, Provider

client = create_client(
    capability=Capability.AUDIO_RECOGNITION,
    provider=Provider.GRADIUM,
    model="default",
)

# Transcribe audio file
with open("audio.wav", "rb") as f:
    audio_data = f.read()

result = await client.transcribe(audio_data, input_format="wav")

print(result.content)  # Full transcription
print(f"Duration: {result.usage.duration_s:.2f}s")
print(f"Characters: {result.usage.characters}")
```

### Real-time Streaming

```python
# Stream audio and get real-time transcription
async def audio_generator():
    # Read audio in chunks (e.g., from microphone)
    with open("audio.wav", "rb") as f:
        f.read(44)  # Skip WAV header for PCM
        while chunk := f.read(3840):  # 1920 samples * 2 bytes = 80ms
            yield chunk

# Receive transcription chunks as they're generated
async for chunk in client.transcribe_stream(audio_generator(), input_format="pcm"):
    print(f"[{chunk.start_s:.2f}s] {chunk.content}")
```

## Configuration

### API Key

Set via environment variable (recommended):
```bash
export GRADIUM_API_KEY=your_api_key_here
```

Or pass directly to the client:
```python
from pydantic import SecretStr

client = create_client(
    capability=Capability.AUDIO_RECOGNITION,
    provider=Provider.GRADIUM,
    model="default",
    api_key=SecretStr("your_api_key"),
)
```

### Region Selection

Choose your region for optimal latency:

```python
from celeste_audio_recognition.providers.gradium.client import GradiumAudioRecognitionClient

client = GradiumAudioRecognitionClient(
    model="default",
    region="eu",  # or "us"
)
```

- `eu`: Europe (default) - `wss://eu.api.gradium.ai/api/speech/asr`
- `us`: United States - `wss://us.api.gradium.ai/api/speech/asr`

## Supported Parameters

### Model

Currently supported model:
- `default`: Gradium's latest STT model

### Input Formats

| Format | Sample Rate | Bit Depth | Channels | Use Case |
|--------|-------------|-----------|----------|----------|
| **pcm** | 24kHz | 16-bit | Mono | Real-time streaming, lowest latency |
| **wav** | Any | Any | Any | General purpose files |
| **opus** | Variable | Variable | Any | Compressed network streaming |

### Audio Specifications for PCM

When using `input_format="pcm"`:
- **Sample Rate**: 24000 Hz (24kHz)
- **Format**: PCM (Pulse Code Modulation)
- **Bit Depth**: 16-bit signed integer (little-endian)
- **Channels**: 1 (mono)
- **Chunk Size**: 1920 samples per chunk (80ms at 24kHz)
- **Bytes per chunk**: 3840 bytes (1920 samples × 2 bytes)

## Response Structure

### Output

```python
result = await client.transcribe(audio_data, input_format="wav")

# Transcribed text
result.content  # str: "Hello, world!"

# Usage metrics
result.usage.characters  # int: Number of characters
result.usage.duration_s  # float: Audio duration in seconds

# Metadata
result.metadata['request_id']  # str: Unique request identifier
result.metadata['sample_rate']  # int: Audio sample rate (24000)
result.metadata['region']  # str: Region used ("eu" or "us")
result.metadata['segments']  # list: Transcription segments with timestamps
result.metadata['vad_steps']  # list: Voice Activity Detection data
```

### Segments

Each segment contains:
```python
{
    'text': str,        # Transcribed text for this segment
    'start_s': float,   # Start time in seconds
    'stop_s': float,    # End time in seconds
    'stream_id': int    # Stream identifier (for multi-stream scenarios)
}
```

### VAD (Voice Activity Detection)

Each VAD step contains:
```python
{
    'vad': [
        {
            'horizon_s': float,         # Lookahead duration (0.5s, 1.0s, 2.0s)
            'inactivity_prob': float    # Probability of silence (0.0-1.0)
        },
        ...
    ],
    'step_idx': int,              # Step index
    'step_duration_s': float,     # Duration of this step (typically 0.08s)
    'total_duration_s': float     # Total audio duration processed
}
```

Use `vad[2]['inactivity_prob']` (2-second horizon) to detect turn completion.

## Streaming Details

### Chunk Format

When using `transcribe_stream()`, you receive `AudioRecognitionChunk` objects:

```python
chunk.content       # str: Transcribed text
chunk.start_s       # float: Start timestamp
chunk.stop_s        # float: End timestamp (may be None)
chunk.stream_id     # int: Stream identifier
```

### WebSocket Protocol

The Gradium STT uses WebSocket for real-time communication:

1. **Setup**: Client sends model and format configuration
2. **Ready**: Server confirms connection and sends parameters
3. **Audio**: Client streams audio chunks
4. **Text**: Server streams transcription chunks as they're generated
5. **VAD**: Server sends Voice Activity Detection updates every 80ms
6. **End**: Client signals end of audio, server sends final results

### Best Practices

1. **Chunk Size**: Use 80ms chunks (3840 bytes for PCM) for optimal performance
2. **Real-time**: Stream audio as it's captured for lowest latency
3. **VAD Monitoring**: Watch `inactivity_prob` to detect speech pauses
4. **Error Handling**: Implement reconnection logic for network issues
5. **Format Choice**:
   - Use **PCM** for real-time applications (mic, live streams)
   - Use **WAV** for file-based transcription
   - Use **Opus** for bandwidth-constrained scenarios

## Supported Languages

Gradium automatically detects and transcribes:
- 🇬🇧 English (en)
- 🇫🇷 French (fr)
- 🇩🇪 German (de)
- 🇪🇸 Spanish (es)
- 🇵🇹 Portuguese (pt)

More languages coming soon!

## Example: Microphone Streaming

```python
import pyaudio
from collections.abc import AsyncGenerator

# Audio configuration
SAMPLE_RATE = 24000  # Hz
CHUNK_SIZE = 1920    # samples (80ms)
CHANNELS = 1         # mono
FORMAT = pyaudio.paInt16  # 16-bit PCM

async def microphone_stream() -> AsyncGenerator[bytes, None]:
    """Stream audio from microphone."""
    audio = pyaudio.PyAudio()

    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
    )

    try:
        while True:
            audio_chunk = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            yield audio_chunk
            await asyncio.sleep(0)  # Allow other tasks
    finally:
        stream.close()
        audio.terminate()

# Transcribe from microphone
async for chunk in client.transcribe_stream(microphone_stream(), input_format="pcm"):
    print(f"[{chunk.start_s:.2f}s] {chunk.content}")
```

## Troubleshooting

### Connection Issues

**Problem**: WebSocket connection fails
**Solution**:
- Verify API key is correct
- Check region selection (try both `eu` and `us`)
- Ensure firewall allows WebSocket connections

### No Transcription Results

**Problem**: Audio sent but no text received
**Solution**:
- Verify audio format matches `input_format` parameter
- For PCM: ensure 24kHz, 16-bit, mono
- Check audio actually contains speech
- Enable debug logging to see WebSocket messages

### Poor Transcription Quality

**Problem**: Incorrect or missing words
**Solution**:
- Use higher quality audio (24kHz minimum)
- Reduce background noise
- Ensure microphone is close to speaker
- For streaming: maintain consistent chunk size (80ms)

## Technical Specifications

- **Protocols**: WebSocket (WSS)
- **Authentication**: API key via `x-api-key` header
- **Endpoints**:
  - EU: `wss://eu.api.gradium.ai/api/speech/asr`
  - US: `wss://us.api.gradium.ai/api/speech/asr`
- **Message Format**: JSON
- **Audio Encoding**: Base64 for WebSocket transport

## Credits and Billing

Gradium charges based on audio duration:
- Billed per second of audio processed
- Real-time streaming and batch transcription priced equally
- See [Gradium Pricing](https://gradium.ai/pricing) for details

## Support

For issues or questions about the Gradium provider:
- **Celeste Integration**: [GitHub Issues](https://github.com/withceleste/celeste-python/issues)
- **Gradium API**: [support@gradium.ai](mailto:support@gradium.ai)
- **Documentation**: [Gradium API Docs](https://gradium.ai/docs)
