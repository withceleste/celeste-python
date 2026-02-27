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

# One SDK. Every modality. Any provider.
text   = await celeste.text.generate("Explain quantum computing", model="claude-opus-4-5")
image  = await celeste.images.generate("A serene mountain lake at dawn", model="flux-2-pro")
speech = await celeste.audio.speak("Welcome to the future", model="eleven_v3")
video  = await celeste.videos.analyze(video_file, prompt="Summarize this clip", model="gemini-3-pro")
embeddings = await celeste.text.embed(["lorep ipsum", "dolor sit amet"], model="gemini-embedding-001")
```



---

<div align="center">

## 15+ providers. Zero lock-in.





<img src="https://www.google.com/favicon.ico" width="32" height="32" alt="Google" title="Google">
<img src="https://www.google.com/s2/favicons?domain=openai.com&sz=64" width="32" height="32" alt="OpenAI" title="OpenAI">
<img src="https://mistral.ai/favicon.ico" width="32" height="32" alt="Mistral" title="Mistral">
<img src="https://www.anthropic.com/favicon.ico" width="32" height="32" alt="Anthropic" title="Anthropic">
<img src="https://cohere.com/favicon.ico" width="32" height="32" alt="Cohere" title="Cohere">
<img src="https://x.ai/favicon.ico" width="32" height="32" alt="xAI" title="xAI">
<img src="https://www.google.com/s2/favicons?domain=deepseek.com&sz=32" width="32" height="32" alt="DeepSeek" title="DeepSeek">
<img src="https://ollama.com/public/apple-touch-icon.png" width="32" height="32" alt="Ollama" title="Ollama">
<img src="https://www.google.com/s2/favicons?domain=groq.com&sz=32" width="32" height="32" alt="Groq" title="Groq">
<img src="https://www.google.com/s2/favicons?domain=elevenlabs.io&sz=32" width="32" height="32" alt="ElevenLabs" title="ElevenLabs">
<img src="https://www.google.com/s2/favicons?domain=seed.bytedance.com&sz=32" width="32" height="32" alt="BytePlus" title="BytePlus">
<img src="https://www.google.com/s2/favicons?domain=blackforestlabs.ai&sz=32" width="32" height="32" alt="Black Forest Labs" title="Black Forest Labs">


**and many more**

**Missing a provider?** [Request it](https://github.com/withceleste/celeste-python/issues/new) – ⚡ **we ship fast**.

</div>

---


## Operations by Domain

| Action | Text | Images | Audio | Video |
| :--- | :---: | :---: | :---: | :---: |
| **Generate** | ✓ | ✓ | ○ | ✓ |
| **Edit** | — | ✓ | — | — |
| **Analyze** | — | ✓ | ✓ | ✓ |
| **Upscale** | — | ○ | — | ○ |
| **Speak** | — | — | ✓ | — |
| **Transcribe** | — | — | ✓ | — |
| **Embed** | ✓ | ○ | — | ○ |

<sub>✓ Available · ○ Planned</sub>


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


## ⚙️ Advanced: Create Client
For explicit configuration or client reuse, use `create_client` with modality + operation. This is modality-first: you choose the output type and operation explicitly.

```python
from celeste import create_client, Modality, Operation, Provider

client = create_client(
    modality=Modality.TEXT,
    operation=Operation.GENERATE,
    provider=Provider.OLLAMA,
    model="llama3.2",
)
response = await client.generate("Extract user info: John is 30", output_schema=User)
```

> `capability` is still supported but deprecated. Prefer `modality` + `operation`.

### Using Google Vertex AI

Celeste supports Google's Vertex AI platform for enterprise-scale AI deployments. Vertex AI requires authentication via Google Cloud credentials.

📓 **[See full example notebook](notebooks/vertexai-example.ipynb)**

**Setup:**

1. Configure your Google Cloud project in `.env`:

```bash
# .env file
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=global  # or us-central1, europe-west4, etc.
```

2. Authenticate using one of these methods:
   - **Application Default Credentials (recommended)**: Run `gcloud auth application-default login`
   - **Service Account**: Set `GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json`

**Usage:**

```python
import os
from celeste import create_client, Modality, Operation, Provider
from celeste.providers.google.auth import GoogleADC
from dotenv import load_dotenv

load_dotenv()

client = create_client(
    modality=Modality.TEXT,
    operation=Operation.GENERATE,
    provider=Provider.GOOGLE,
    model="gemini-3.1-pro-preview",
    auth=GoogleADC(
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION")
    )
)

# Use built-in web search (grounded generation)
response = await client.generate(
    "Explain quantum computing with citation links",
    web_search=True
)
print(response.content)
```

See [.env.example](.env.example) for complete Vertex AI configuration options.

### Using OpenAI/Anthropic-Compatible APIs

Celeste cannot cover every AI provider in existence. However, many providers offer OpenAI-compatible or Anthropic-compatible APIs without releasing their own SDKs. Example: **[MiniMax](https://platform.minimax.io/docs/guides/text-generation)**.

📓 **[See full example notebook](notebooks/anthropic_compat.ipynb)**

> ⚠️ **Warning:** Always check the provider's documentation first to confirm whether they are compatible with OpenAI or Anthropic APIs. Not all providers support the same endpoints or features.

For Anthropic-compatible providers, you can configure a custom base URL using the `ANTHROPIC_BASE_URL` environment variable:

```bash
# .env file
ANTHROPIC_API_KEY=your-minimax-api-key-here
ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
```

Then use it like any Anthropic model:

```python
import os
from celeste import create_client, Modality, Operation, Provider
from dotenv import load_dotenv

load_dotenv()

client = create_client(
    modality=Modality.TEXT,
    operation=Operation.GENERATE,
    provider=Provider.ANTHROPIC,
    model="MiniMax-M2.5",  # Custom model ID
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

response = await client.generate("Explain quantum computing")
print(response.content)
```

> **Note:** You may see a warning like `Model 'MiniMax-M2.5' not registered in Celeste`. This is expected—parameter validation is disabled, but the API call works normally.

**Optional: Register Custom Models**

To eliminate the warning and enable parameter validation, you can register custom models:

```python
from celeste.models import Model, register_models
from celeste.constraints import Range
from celeste import Modality, Operation, Provider

minimax_model = Model(
    id="MiniMax-M2.5",
    provider=Provider.ANTHROPIC,
    display_name="MiniMax M2.5",
    operations={Modality.TEXT: {Operation.GENERATE}},
    streaming=True,
    parameter_constraints={
        "temperature": Range(min=0.0, max=1.0),
        "max_tokens": Range(min=1, max=4096),
    }
)

register_models([minimax_model])
```

After registration, parameter validation will be enabled for the custom model.

Similarly, for OpenAI-compatible providers, use the `OPENAI_BASE_URL` environment variable:

```bash
# .env file
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://your-openai-compatible-endpoint.com
```

Then use it with the OpenAI provider:

```python
from celeste import create_client, Modality, Operation, Provider

client = create_client(
    modality=Modality.TEXT,
    operation=Operation.GENERATE,
    provider=Provider.OPENAI,
    model="your-custom-model-id"
)

response = await client.generate("Your prompt here")
```

See [.env.example](.env.example) for all available `*_BASE_URL` configuration options.

---
## 🪶 Install
```bash
uv add celeste-ai
# or
pip install celeste-ai
```

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



<div align="center">

**[Get Started](https://withceleste.ai/docs/quickstart)** • **[Documentation](https://withceleste.ai/docs)** • **[GitHub](https://github.com/withceleste/celeste-python)**

Made with ❤️ by developers tired of framework lock-in

</div>
