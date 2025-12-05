<div align="center">

# <img src="../../logo.svg" width="48" height="48" alt="Celeste Logo" style="vertical-align: middle;"> Celeste Music Generation

**Music Generation capability for Celeste AI**

[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-red?style=for-the-badge)](../../LICENSE)

[Quick Start](#-quick-start) • [Documentation](https://withceleste.ai/docs) • [Request Provider](https://github.com/withceleste/celeste-python/issues/new)

</div>

---

## 🚀 Quick Start

```python
from celeste import create_client, Capability, Provider

client = create_client(
    capability=Capability.MUSIC_GENERATION,
    provider=Provider.MUREKA,
)

response = await client.generate(prompt="Upbeat electronic music with a driving beat")
print(response.content)
```

**Install:**
```bash
uv add "celeste-ai[music-generation]"
```

---

## Supported Providers


<div align="center">

<img src="https://www.google.com/s2/favicons?domain=mureka.ai&sz=64" width="64" height="64" alt="Mureka" title="Mureka">


**Missing a provider?** [Request it](https://github.com/withceleste/celeste-python/issues/new) – ⚡ **we ship fast**.

</div>

---

## Features

### Async Task-Based Generation

Mureka uses an asynchronous task-based API:
1. Submit generation request → receive task ID
2. Automatic polling until completion
3. Retrieve final audio URL

### Streaming Support

Enable progressive streaming for supported models:
```python
response = await client.generate(
    prompt="Relaxing ambient music",
    stream=True,
    duration=60  # seconds
)
```

### Rich Parameters

- **Duration**: Control track length (5-600 seconds)
- **Style & Genre**: Specify musical style and genre
- **Tempo & Key**: Set BPM and musical key
- **Mood**: Define emotional tone
- **Lyrics**: Add custom lyrics with vocal options
- **Quality**: Choose from standard to premium quality

---

## 🎵 Example Usage

### Generate Instrumental

```python
response = await client.generate(
    prompt="Epic orchestral soundtrack",
    duration=120,
    instrumental_only=True,
    tempo=140,
    key="D minor"
)
```

### Generate with Lyrics

```python
response = await client.generate(
    prompt="Pop song about summer",
    lyrics="Summer days and endless nights...",
    vocal_gender="female",
    vocal_style="pop",
    duration=180
)
```

### Advanced Parameters

```python
response = await client.generate(
    prompt="Jazz fusion track",
    genre="jazz",
    tempo=120,
    key="C major",
    mood="relaxed",
    quality="premium",
    duration=240
)
```

---

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
