<div align="center">

# Celeste AI

<img src="https://raw.githubusercontent.com/withceleste/celeste-python/main/logo.svg" width="64" height="64" alt="Celeste Logo">

**The primitive layer for multi-modal AI**

All modalities. All providers. One interface.

Primitives, not frameworks.

[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/celeste-ai?style=for-the-badge)](https://pypi.org/project/celeste-ai/)

<a href="https://github.com/withceleste/celeste-python" target="_parent">
  <img alt="" src="https://img.shields.io/github/stars/withceleste/celeste-python.svg?style=social&label=Star" alt="GitHub stars" />
</a>
<a href="https://pypi.org/project/celeste-ai" target="_parent">
  <img alt="" src="https://img.shields.io/pypi/dm/celeste-ai.svg" />
</a>
<a href="https://www.linkedin.com/company/withceleste" target="_parent">
  <img src="https://img.shields.io/badge/LinkedIn-Follow%20%40withceleste-0077B5?style=social&logo=linkedin&logoColor=white" alt="Follow @withceleste on LinkedIn"/>
</a>

[Quick Start](#-quick-start) • [Request Provider](https://github.com/withceleste/celeste-python/issues/new)

</div>

> 🚀 This is the v1 Beta release. We're validating the new architecture before the stable v1.0 release. Feedback welcome!

# Celeste AI

Type-safe, modality/provider-agnostic primitives.

- **Unified Interface:** One API for OpenAI, Anthropic, Gemini, Mistral, and 14+ others.
- **True Multi-Modal:** Text, Image, Audio, Video, Embeddings, Search —all first-class citizens.
- **Type-Safe by Design:** Full Pydantic validation and IDE autocomplete.
- **Zero Lock-In:** Switch providers instantly by changing a single config string.
- **Primitives, Not Frameworks:** No agents, no chains, no magic. Just clean I/O.
- **Lightweight Architecture:** No vendor SDKs. Pure, fast HTTP.

## 🚀 Quick Start
```python
import celeste

# "We need a catchy slogan for our new eco-friendly sneaker."
slogan = await celeste.text.generate(
    "Write a slogan for an eco-friendly sneaker.",
    model="gpt-5",
)
print(slogan.content)
```


## 🎨 Multimodal example
```python
import celeste
from pydantic import BaseModel, Field

class ProductCampaign(BaseModel):
    visual_prompt: str
    audio_script: str

# 2. Extract Campaign Assets (Anthropic)
# -----------------------------------------------------
campaign_output = await celeste.text.generate(
    f"Create campaign assets for slogan: {slogan.content}",
    model="claude-opus-4-1",
    output_schema=ProductCampaign,
)
campaign = campaign_output.content

# 3. Generate Ad Visual (Flux)
# -----------------------------------------------------
image_output = await celeste.images.generate(
    campaign.visual_prompt,
    model="flux-2-flex",
    aspect_ratio="1:1"
)
image = image_output.content

# 4. Generate Radio Spot (ElevenLabs)
# -----------------------------------------------------
speech_output = await celeste.audio.speak(
    campaign.audio_script,
    model="eleven_v3",
    voice="adam"
)
speech = speech_output.content
```

No special cases. No separate libraries. **One consistent interface.**



---

<div align="center">

## 15+ providers. Zero lock-in.





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

## 🔄 Switch providers in one line


```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

# Model IDs
anthropic_model_id = "claude-4-5-sonnet"
google_model_id = "gemini-2.5-flash"
```

```python
# ❌ Anthropic Way
from anthropic import Anthropic
import json

client = Anthropic()
response = client.messages.create(
    model=anthropic_model_id,
    messages=[
        {"role": "user",
         "content": "Extract user info: John is 30"}
    ],
    output_format={
        "type": "json_schema",
        "schema": User.model_json_schema()
    }
)
user_data = json.loads(response.content[0].text)
```

```python
# ❌ Google Gemini Way
from google import genai
from google.genai import types

client = genai.Client()
response = await client.aio.models.generate_content(
    model=gemini_model_id,
    contents="Extract user info: John is 30",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=User
    )
)
user = response.parsed
```

```python
# ✅ Celeste Way
import celeste

response = await celeste.text.generate(
    "Extract user info: John is 30",
    model=google_model_id,  # <--- Choose any model from any provider
    output_schema=User,  # <--- Unified parameter working across all providers
)
user = response.content  # Already parsed as User instance
```

---
## 🧭 Namespace API (recommended)
Namespaces are domain-first: start from the resource you want to work with (e.g., videos) even if the input is text. Under the hood, Celeste maps (domain, operation) to the output modality (e.g., `celeste.images.analyze(...)` routes to the text modality because analysis returns text).
```python
import celeste

# Async (default)
result = await celeste.images.analyze(
    image=img,
    prompt="Describe this image",
    model="gpt-4o"
)

# Sync
result = celeste.images.sync.analyze(
    image=img,
    prompt="Describe this image",
    model="gpt-4o"
)

# Async streaming
async for chunk in celeste.text.stream.generate("Hello", model="gpt-4o"):
    print(chunk.content, end="")

# Sync streaming
for chunk in celeste.text.sync.stream.generate("Hello", model="gpt-4o"):
    print(chunk.content, end="")
```

---
## ⚙️ Advanced: create_client
For explicit configuration or client reuse, use `create_client` with modality + operation. This is modality-first: you choose the output type and operation explicitly.

```python
from celeste import create_client, Modality, Operation

client = create_client(
    modality=Modality.TEXT,
    operation=Operation.GENERATE,
    model=google_model_id,
)
response = await client.generate("Extract user info: John is 30", output_schema=User)
```

> `capability` is still supported but deprecated. Prefer `modality` + `operation`.

---
## 🪶 Install
```bash
pip install celeste-ai
# or
uv add celeste-ai
```
---
## 🔁 Behavior changes since v0.3.9
- Capabilities → modalities + operations.
- Namespace API is now the default entry point.
- `create_client` now uses `modality` + `operation`; `capability` is deprecated.
- `analyze` for image/audio/video routes through the text modality.
- Namespaces are domain-first (resource you work with); `create_client` is modality-first (output type). Domain + operation maps to modality.
- `extra_body` allows provider-specific parameters without first-class mapping.
- Single-package install (no extras).

---
## 🔧 Type-Safe by Design

```python
# Full IDE autocomplete
import celeste

response = await celeste.text.generate(
    "Explain AI",
    model="gpt-4o-mini",
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

MIT license – see [LICENSE](LICENSE) for details.

---

<div align="center">

**[Get Started](https://withceleste.ai/docs/quickstart)** • **[Documentation](https://withceleste.ai/docs)** • **[GitHub](https://github.com/withceleste/celeste-python)**

Made with ❤️ by developers tired of framework lock-in

</div>
