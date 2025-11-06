<div align="center">

# Celeste AI

<img src="https://raw.githubusercontent.com/withceleste/celeste-python/main/logo.svg" width="64" height="64" alt="Celeste Logo">

**The primitive layer for multi-modal AI**

All capabilities. All providers. One interface.

Primitives, not frameworks.

[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-red?style=for-the-badge)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-celeste--ai-green?style=for-the-badge)](https://pypi.org/project/celeste-ai/)

[Quick Start](#-quick-start) • [Request Provider](https://github.com/withceleste/celeste-python/issues/new)

</div>

---

## 🚀 Quick Start

```python
from celeste import create_client, Capability, Provider

# Create client
client = create_client(
    capability=Capability.TEXT_GENERATION,
    provider=Provider.ANTHROPIC,
    api_key="your-api-key",  # Or loads automatically from environment
)

# Generate
response = await client.generate(prompt="Explain quantum computing")
print(response.content)
```

**Install:**
```bash
uv add "celeste-ai[text-generation]"  # Text only
uv add "celeste-ai[image-generation]" # Image generation
uv add "celeste-ai[all]"              # Everything
```

---

## 🎨 Multi-Modal Example

```python
# Same API, different modalities
text_client = create_client(Capability.TEXT_GENERATION, Provider.ANTHROPIC)
image_client = create_client(Capability.IMAGE_GENERATION, Provider.OPENAI)
video_client = create_client(Capability.VIDEO_GENERATION, Provider.GOOGLE)

text = await text_client.generate(prompt="Write a haiku about AI")
image = await image_client.generate(prompt="A sunset over mountains")
video = await video_client.generate(prompt="Waves crashing on a beach")
```

No special cases. No separate libraries. **One consistent interface.**

---


<div align="center">

<img src="https://www.google.com/favicon.ico" width="32" height="32" alt="Google" title="Google">
<img src="https://www.anthropic.com/favicon.ico" width="32" height="32" alt="Anthropic" title="Anthropic">
<img src="https://www.google.com/s2/favicons?domain=openai.com&sz=64" width="32" height="32" alt="OpenAI" title="OpenAI">
<img src="https://mistral.ai/favicon.ico" width="32" height="32" alt="Mistral" title="Mistral">
<img src="https://cohere.com/favicon.ico" width="32" height="32" alt="Cohere" title="Cohere">
<img src="https://x.ai/favicon.ico" width="32" height="32" alt="xAI" title="xAI">
<img src="https://www.google.com/s2/favicons?domain=deepseek.com&sz=32" width="32" height="32" alt="DeepSeek" title="DeepSeek">
<img src="https://www.google.com/s2/favicons?domain=groq.com&sz=32" width="32" height="32" alt="Groq" title="Groq">
<img src="https://www.google.com/s2/favicons?domain=perplexity.ai&sz=32" width="32" height="32" alt="Perplexity" title="Perplexity">
<img src="https://ollama.com/public/apple-touch-icon.png" width="32" height="32" alt="Ollama" title="Ollama">
<img src="https://huggingface.co/favicon.ico" width="32" height="32" alt="Hugging Face" title="Hugging Face">
<img src="https://www.google.com/s2/favicons?domain=replicate.com&sz=32" width="32" height="32" alt="Replicate" title="Replicate">
<img src="https://www.google.com/s2/favicons?domain=stability.ai&sz=32" width="32" height="32" alt="Stability AI" title="Stability AI">
<img src="https://www.google.com/s2/favicons?domain=runwayml.com&sz=32" width="32" height="32" alt="Runway" title="Runway">
<img src="https://www.google.com/s2/favicons?domain=elevenlabs.io&sz=32" width="32" height="32" alt="ElevenLabs" title="ElevenLabs">

**and many more**

**Missing a provider?** [Request it](https://github.com/withceleste/celeste-python/issues/new) – ⚡ **we ship fast**.

</div>

---

## 🔧 Type-Safe by Design

```python
# Full IDE autocomplete
response = await client.generate(
    prompt="Explain AI",
    temperature=0.7,    # ✅ Validated (0.0-2.0)
    max_tokens=100,     # ✅ Validated (int)
)

# Typed response
print(response.content)              # str (IDE knows the type)
print(response.usage.input_tokens)   # int
print(response.metadata["model"])     # str
```

Catch errors **before** production.

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

**Request a provider:** [GitHub Issues](https://github.com/withceleste/celeste-python/issues/new)
**Report bugs:** [GitHub Issues](https://github.com/withceleste/celeste-python/issues)

---

## 📄 License

Apache 2.0 license – see [LICENSE](LICENSE) for details.

---

<div align="center">

**[Get Started](https://withceleste.ai/docs/quickstart)** • **[Documentation](https://withceleste.ai/docs)** • **[GitHub](https://github.com/withceleste/celeste-python)**

Made with ❤️ by developers tired of framework lock-in

</div>
