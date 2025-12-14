<div align="center">

# <img src="../../logo.svg" width="48" height="48" alt="Celeste Logo" style="vertical-align: middle;"> Celeste Speech Generation

**Speech Generation capability for Celeste AI**

[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](../../../LICENSE)

[Quick Start](#-quick-start) • [Documentation](https://withceleste.ai/docs) • [Request Provider](https://github.com/withceleste/celeste-python/issues/new)

</div>

---

## 🚀 Quick Start

```python
from celeste import create_client, Capability, Provider

client = create_client(
    capability=Capability.SPEECH_GENERATION,
    provider=Provider.ELEVENLABS,
)

response = await client.generate(text="Welcome to Celeste AI. Transform your text into natural, expressive speech with just a few lines of code.")
# response.content is an AudioArtifact with binary audio data
```

**Install:**
```bash
uv add "celeste-ai[speech-generation]"
```

---

## Supported Providers


<div align="center">

<img src="https://www.google.com/s2/favicons?domain=openai.com&sz=64" width="64" height="64" alt="OpenAI" title="OpenAI">
<img src="https://www.google.com/s2/favicons?domain=google.com&sz=64" width="64" height="64" alt="Google" title="Google">
<img src="https://www.google.com/s2/favicons?domain=elevenlabs.io&sz=64" width="64" height="64" alt="ElevenLabs" title="ElevenLabs">


**Missing a provider?** [Request it](https://github.com/withceleste/celeste-python/issues/new) – ⚡ **we ship fast**.

</div>

---

**Streaming**: ✅ Supported

**Parameters**: See [API Documentation](https://withceleste.ai/docs/api) for full parameter reference.

---

## 🤝 Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

**Request a provider:** [GitHub Issues](https://github.com/withceleste/celeste-python/issues/new)

---

## 📄 License

MIT License – see [LICENSE](../../../LICENSE) for details.

---

<div align="center">

**[Get Started](https://withceleste.ai/docs/quickstart)** • **[Documentation](https://withceleste.ai/docs)** • **[GitHub](https://github.com/withceleste/celeste-python)**

Made with ❤️ by developers tired of framework lock-in

</div>
