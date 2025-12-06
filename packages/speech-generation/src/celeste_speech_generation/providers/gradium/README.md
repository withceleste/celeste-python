# Gradium TTS Provider

Gradium is a high-quality text-to-speech provider with low-latency streaming capabilities and multi-language support.

## Features

- **WebSocket Streaming**: Real-time audio generation with chunked delivery
- **14 Flagship Voices**: Professional voices across 5 languages (English, French, German, Spanish, Portuguese)
- **Custom Voice Cloning**: Create personalized voices from audio samples
- **Speed Control**: Adjust speech rate from -4.0 (faster) to 4.0 (slower)
- **Multiple Audio Formats**: wav, pcm, opus, ulaw_8000, alaw_8000, pcm_16000, pcm_24000
- **Regional Endpoints**: EU and US regions for optimized latency
- **Credits Monitoring**: Track usage and billing information

## Setup

### API Key

Get your API key from [Gradium](https://gradium.ai) and add it to your `.env` file:

```bash
GRADIUM_API_KEY=your-gradium-api-key-here
```

### Installation

```bash
pip install celeste-ai[speech-generation]
```

The Gradium provider requires the `websockets` package, which is included in Celeste's dependencies.

## Basic Usage

```python
from celeste import Capability, Provider, create_client

# Create client
client = create_client(
    capability=Capability.SPEECH_GENERATION,
    provider=Provider.GRADIUM,
    model="default",
)

# Generate speech
result = await client.generate(
    "Hello! Welcome to Gradium text-to-speech."
)

# Save audio
with open("output.wav", "wb") as f:
    f.write(result.content.data)
```

## Available Voices

Gradium provides 14 flagship voices across multiple languages:

### English Voices
- **Emma** (en-US) - Female, pleasant and smooth
- **Kent** (en-US) - Male, trustworthy and warm
- **Sydney** (en-US) - Female, energetic and friendly
- **John** (en-US) - Male, deep and authoritative
- **Eva** (en-GB) - Female, refined British accent
- **Jack** (en-GB) - Male, sophisticated British accent

### French Voices
- **Elise** (fr-FR) - Female, elegant Parisian
- **Leo** (fr-FR) - Male, sophisticated and clear

### German Voices
- **Mia** (de-DE) - Female, precise and articulate
- **Maximilian** (de-DE) - Male, strong and professional

### Spanish Voices
- **Valentina** (es-ES) - Female, warm Castilian
- **Sergio** (es-MX) - Male, friendly Mexican

### Portuguese Voices
- **Alice** (pt-BR) - Female, vibrant Brazilian
- **Davi** (pt-BR) - Male, confident Brazilian

## Voice Selection

```python
# Use a specific voice
result = await client.generate(
    "Bonjour! Bienvenue chez Gradium.",
    voice="b35yykvVppLXyw_l",  # Elise (French)
)

# Default voice is Emma (en-US) if not specified
result = await client.generate("Hello!")
```

## Speed Control

Adjust speech rate using the `speed` parameter (padding_bonus in Gradium API):

```python
# Faster speech (negative values)
result = await client.generate(
    "This will be spoken faster.",
    voice="YTpq7expH9539ERJ",
    speed=-2.0,
)

# Normal speed (default)
result = await client.generate(
    "This will be spoken at normal speed.",
    speed=0.0,
)

# Slower speech (positive values)
result = await client.generate(
    "This will be spoken slower.",
    speed=2.0,
)
```

Speed range: `-4.0` (faster) to `4.0` (slower)

## Audio Formats

Gradium supports multiple output formats:

```python
# WAV format (default)
result = await client.generate(
    "Hello!",
    response_format="wav",
)

# Raw PCM
result = await client.generate(
    "Hello!",
    response_format="pcm",
)

# Opus (compressed)
result = await client.generate(
    "Hello!",
    response_format="opus",
)

# Other formats: ulaw_8000, alaw_8000, pcm_16000, pcm_24000
```

## Region Configuration

Select EU or US region for optimized latency:

```python
from celeste_speech_generation.providers.gradium import GradiumSpeechGenerationClient

# EU region (default)
client = GradiumSpeechGenerationClient(
    region="eu",
    model="default",
)

# US region
client = GradiumSpeechGenerationClient(
    region="us",
    model="default",
)
```

## Voice Management

### List Voices

```python
# List your custom voices
voices = await client.list_voices(limit=10)
for voice in voices:
    print(f"{voice.name} ({voice.uid})")

# Include catalog voices
all_voices = await client.list_voices(
    limit=20,
    include_catalog=True,
)
```

### Get Voice Details

```python
voice = await client.get_voice("voice-uid-here")
print(f"Name: {voice.name}")
print(f"Language: {voice.language}")
print(f"Description: {voice.description}")
```

### Create Custom Voice

```python
# From file path
response = await client.create_voice(
    audio_file="/path/to/audio.wav",
    name="My Custom Voice",
    description="A unique voice for my brand",
    language="en-US",
    input_format="wav",
    start_s=0.0,
    timeout_s=10.0,
)
print(f"Created voice: {response.uid}")

# From bytes
with open("audio.wav", "rb") as f:
    audio_data = f.read()

response = await client.create_voice(
    audio_file=audio_data,
    name="My Custom Voice",
)
```

### Update Voice

```python
updated_voice = await client.update_voice(
    voice_uid="voice-uid-here",
    name="Updated Name",
    description="Updated description",
)
```

### Delete Voice

```python
await client.delete_voice("voice-uid-here")
```

## Credits Monitoring

Track your API usage and billing:

```python
credits = await client.get_credits()

print(f"Plan: {credits.plan_name}")
print(f"Remaining: {credits.remaining_credits:,} credits")
print(f"Allocated: {credits.allocated_credits:,} credits")
print(f"Billing period: {credits.billing_period}")
print(f"Next rollover: {credits.next_rollover_date}")

# Calculate usage percentage
if credits.allocated_credits > 0:
    used = credits.allocated_credits - credits.remaining_credits
    usage_pct = (used / credits.allocated_credits) * 100
    print(f"Usage: {usage_pct:.1f}%")
```

Gradium charges **1 credit per character** of text processed.

## Complete Example

```python
import asyncio
from pathlib import Path
from celeste import Capability, Provider, create_client

async def main():
    # Create client
    client = create_client(
        capability=Capability.SPEECH_GENERATION,
        provider=Provider.GRADIUM,
        model="default",
    )

    # Generate speech with custom parameters
    result = await client.generate(
        "Welcome to Gradium! This is a demonstration of high-quality text-to-speech.",
        voice="YTpq7expH9539ERJ",  # Emma
        speed=0.0,
        response_format="wav",
    )

    # Check metadata
    print(f"Sample rate: {result.metadata['sample_rate']} Hz")
    print(f"Region: {result.metadata['region']}")
    print(f"Request ID: {result.metadata['request_id']}")

    # Save audio
    output_path = Path("output.wav")
    output_path.write_bytes(result.content.data)
    print(f"Saved to: {output_path}")

    # Check credits
    credits = await client.get_credits()
    print(f"Remaining credits: {credits.remaining_credits:,}")

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### GradiumSpeechGenerationClient

Main client class for Gradium TTS.

#### Methods

**`generate(text, voice=None, speed=0.0, response_format='wav')`**

Generate speech from text.

- `text` (str): Text to convert to speech
- `voice` (str, optional): Voice ID (default: Emma)
- `speed` (float, optional): Speed modifier -4.0 to 4.0 (default: 0.0)
- `response_format` (str, optional): Audio format (default: 'wav')

Returns: `SpeechGenerationOutput` with audio data

**`list_voices(skip=0, limit=100, include_catalog=False)`**

List available voices.

- `skip` (int): Number of voices to skip (pagination)
- `limit` (int): Maximum number of voices to return
- `include_catalog` (bool): Include catalog voices

Returns: `list[VoiceInfo]`

**`get_voice(voice_uid)`**

Get information about a specific voice.

- `voice_uid` (str): Unique identifier of the voice

Returns: `VoiceInfo`

**`create_voice(audio_file, name, input_format='wav', description=None, language=None, start_s=0.0, timeout_s=10.0)`**

Create a custom voice from audio sample.

- `audio_file` (str | bytes): Path to audio file or raw audio bytes
- `name` (str): Name for the voice
- `input_format` (str): Audio format (default: 'wav')
- `description` (str, optional): Description
- `language` (str, optional): Language code
- `start_s` (float): Start time in audio file (seconds)
- `timeout_s` (float): Timeout for voice creation (seconds)

Returns: `VoiceCreateResponse`

**`update_voice(voice_uid, name=None, description=None, language=None, start_s=None)`**

Update a custom voice.

- `voice_uid` (str): Unique identifier of the voice
- `name` (str, optional): New name
- `description` (str, optional): New description
- `language` (str, optional): New language code
- `start_s` (float, optional): New start time

Returns: `VoiceInfo`

**`delete_voice(voice_uid)`**

Delete a custom voice.

- `voice_uid` (str): Unique identifier of the voice

Returns: None

**`get_credits()`**

Get current credit balance and usage information.

Returns: `CreditsSummary`

### Data Models

**VoiceInfo**

```python
uid: str                      # Unique identifier
name: str                     # Voice name
description: str | None       # Optional description
language: str | None          # Language code (e.g., 'en-US')
start_s: float                # Start time in audio sample
stop_s: float | None          # Stop time in audio sample
filename: str                 # Audio file name
```

**VoiceCreateResponse**

```python
uid: str | None               # Created voice UID
error: str | None             # Error message if failed
was_updated: bool             # Whether voice was updated
```

**CreditsSummary**

```python
remaining_credits: int        # Remaining credits
allocated_credits: int        # Total allocated credits
billing_period: str           # Current billing period
next_rollover_date: str | None  # Next credit rollover date
plan_name: str                # Plan name
```

## WebSocket Protocol

Gradium uses WebSocket for real-time TTS streaming. The client handles the protocol automatically:

1. **Setup Message**: Configures voice, model, and output format
2. **Ready Message**: Server confirms setup and provides request ID
3. **Text Message**: Client sends text to synthesize
4. **Audio Messages**: Server streams base64-encoded audio chunks
5. **End of Stream**: Signals completion

The audio chunks are automatically decoded and concatenated into a single audio file.

## Error Handling

```python
try:
    result = await client.generate("Hello!")
except RuntimeError as e:
    # WebSocket connection errors
    print(f"Connection error: {e}")
except ValueError as e:
    # Invalid parameters or response format
    print(f"Validation error: {e}")
except Exception as e:
    # Other errors
    print(f"Unexpected error: {e}")
```

## Limitations

- Maximum text length: Check your plan limits
- Voice cloning requires high-quality audio samples (clean, clear speech)
- Custom voices may take a few seconds to process
- Credits are consumed on successful generation (1 credit = 1 character)

## Resources

- [Gradium Website](https://gradium.ai)
- [Gradium Documentation](https://docs.gradium.ai)
- [API Reference](https://api.gradium.ai/docs)

## Support

For issues specific to the Celeste Gradium integration, please open an issue on the [Celeste GitHub repository](https://github.com/withceleste/celeste-python/issues).

For Gradium API questions, contact [Gradium support](https://gradium.ai/support).
