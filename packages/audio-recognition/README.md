<div align="center">

# <img src="../../logo.svg" width="48" height="48" alt="Celeste Logo" style="vertical-align: middle;"> Celeste Audio Recognition

**Speech-to-Text (STT) capability for Celeste AI**

[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-red?style=for-the-badge)](../../LICENSE)

[Quick Start](#-quick-start) • [Documentation](https://withceleste.ai/docs) • [Request Provider](https://github.com/withceleste/celeste-python/issues/new)

</div>

---

## 🚀 Quick Start

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
print(result.content)  # Transcribed text
print(f"Duration: {result.usage.duration_s:.2f}s")
```

**Install:**
```bash
uv add "celeste-ai[audio-recognition]"
```

---

## Supported Providers


<div align="center">

<img src="https://www.google.com/s2/favicons?domain=gradium.ai&sz=64" width="64" height="64" alt="Gradium" title="Gradium">


**Missing a provider?** [Request it](https://github.com/withceleste/celeste-python/issues/new) – ⚡ **we ship fast**.

</div>

---

## Features

- 🎤 **Real-time Streaming**: Stream audio and receive transcription chunks as you speak
- 🕐 **Timestamps**: Get precise timing for each word or phrase
- 🔊 **Voice Activity Detection (VAD)**: Automatic speech/silence detection
- 🌍 **Multi-language**: Auto-detect and transcribe multiple languages
- 📊 **Multiple Formats**: Support for PCM, WAV, Opus audio formats

---

## Streaming Example

```python
# Real-time transcription from audio stream
async def audio_generator():
    # Your audio source (file, microphone, etc.)
    with open("audio.wav", "rb") as f:
        f.read(44)  # Skip WAV header for PCM
        while chunk := f.read(3840):  # 80ms chunks
            yield chunk

async for chunk in client.transcribe_stream(audio_generator(), input_format="pcm"):
    print(f"[{chunk.start_s:.2f}s] {chunk.content}")
```

---

## Configuration

Set your API key as an environment variable:

```bash
export GRADIUM_API_KEY=your_api_key_here
```

Or pass it directly:

```python
from pydantic import SecretStr

client = create_client(
    capability=Capability.AUDIO_RECOGNITION,
    provider=Provider.GRADIUM,
    model="default",
    api_key=SecretStr("your_api_key"),
)
```

---

## Supported Audio Formats

| Format | Description | Recommended Use |
|--------|-------------|-----------------|
| **PCM** | Raw 24kHz 16-bit mono | Real-time streaming, lowest latency |
| **WAV** | Standard WAV file | General purpose, easy to use |
| **Opus** | Compressed format | Network streaming, bandwidth optimization |

---

## Provider Details

### Gradium

- **Low Latency**: <300ms time-to-first-token
- **WebSocket Streaming**: Real-time bidirectional communication
- **Voice Activity Detection**: Built-in silence/speech detection
- **Multi-language**: Auto-detect English, French, German, Spanish, Portuguese

See [Gradium provider README](src/celeste_audio_recognition/providers/gradium/README.md) for detailed documentation.

---

**Streaming**: ✅ Supported

**Parameters**: See [API Documentation](https://withceleste.ai/docs/api) for full parameter reference.

---

## 🤝 Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

**Request a provider:** [GitHub Issues](https://github.com/withceleste/celeste-python/issues/new)

---

## 📄 License

Apache 2.0 License – see [LICENSE](../../LICENSE) for details.

---

<div align="center">

**[Get Started](https://withceleste.ai/docs/quickstart)** • **[Documentation](https://withceleste.ai/docs)** • **[GitHub](https://github.com/withceleste/celeste-python)**

Made with ❤️ by developers tired of framework lock-in

</div>
