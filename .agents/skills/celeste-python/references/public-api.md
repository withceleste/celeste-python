# Celeste Public API Reference

Use this for app-side integrations and examples.

## Namespace-First Usage

Normal app code should use public namespaces from `src/celeste/namespaces/domains.py`.

```python
import celeste

text_model = "..."  # choose from celeste.list_models(modality=celeste.Modality.TEXT, ...)
image_model = "..."  # choose from celeste.list_models(modality=celeste.Modality.IMAGES, ...)
audio_model = "..."  # choose from celeste.list_models(modality=celeste.Modality.AUDIO, ...)
video_model = "..."  # choose from celeste.list_models(modality=celeste.Modality.VIDEOS, ...)
video = "..."  # use a video artifact or supported video input

text = await celeste.text.generate("Explain quantum computing", model=text_model)
image = await celeste.images.generate("A mountain lake", model=image_model)
speech = await celeste.audio.speak("Welcome", model=audio_model)
summary = await celeste.videos.analyze(video, prompt="Summarize this clip", model=video_model)
embeddings = await celeste.text.embed(["lorem ipsum"], model=text_model)
```

Available namespace families include:

- `celeste.text.generate`
- `celeste.text.embed`
- `celeste.images.generate`
- `celeste.images.edit`
- `celeste.images.analyze`
- `celeste.images.embed`
- `celeste.audio.speak`
- `celeste.audio.analyze`
- `celeste.audio.embed`
- `celeste.videos.generate`
- `celeste.videos.analyze`
- `celeste.videos.embed`
- `celeste.documents.analyze`

Use sync and streaming namespaces when needed:

- `celeste.text.sync.generate(...)`
- `celeste.text.stream.generate(...)`
- `celeste.images.sync.edit(...)`
- `celeste.audio.stream.speak(...)`

Inspect `src/celeste/namespaces/domains.py` for exact signatures.

## Explicit Client Usage

Use `create_client(...)` for explicit client reuse or lower-level configuration.

```python
from celeste import Modality, Operation, Provider, create_client

model_id = "..."  # choose from model discovery or current provider docs

client = create_client(
    modality=Modality.TEXT,
    operation=Operation.GENERATE,
    provider=Provider.OLLAMA,
    model=model_id,
)
response = await client.generate("Extract user info")
```

Important details:

- Select clients with `modality` + `operation`.
- Use `protocol` and `base_url` for compatible text APIs.
- If `base_url` is provided without provider/protocol, Celeste defaults to the OpenResponses protocol path.
- Unknown provider models can create a fallback model only when provider and modality context make that intentional; check `src/celeste/__init__.py`.

## Model Discovery

Use Celeste model discovery instead of duplicating catalogs:

```python
from celeste import Modality, Operation, Provider, list_models

models = list_models(
    provider=Provider.OPENAI,
    modality=Modality.TEXT,
    operation=Operation.GENERATE,
)
```

Relevant source:

- `src/celeste/models.py`
- `src/celeste/__init__.py`
- `references/verification.md` for focused test selection

## Public Types

Use Celeste-owned types for Celeste concepts. Import paths matter.

- Top-level `celeste`: `Provider`, `Protocol`, `Modality`, `Operation`, `Message`, `MessageContent`, `MessagePart`, `TextPart`, `ImagePart`, `AudioPart`, `VideoPart`, `DocumentPart`, `Role`, `Tool`, `ToolCall`, `WebSearch`, `XSearch`, `CodeExecution`, `ToolChoice`, `ToolResult`, `ToolResultContent`, `ToolOutput`, `ToolError`.
- `celeste.core`: `InputType`, `Domain`, `Parameter`, `UsageField`, and other core enums not exported from the root package.
- `celeste.artifacts`: `ImageArtifact`, `VideoArtifact`, `AudioArtifact`, `DocumentArtifact`.
- `celeste.mime_types`: `ImageMimeType`, `VideoMimeType`, `AudioMimeType`, `DocumentMimeType`, `ApplicationMimeType`.

Do not replace these with app-local enums or raw strings unless the code is truly app-specific transport.

## Artifacts And MIME Types

Artifacts support `url`, `data`, and `path`.

```python
from celeste.artifacts import ImageArtifact
from celeste.mime_types import ImageMimeType

image = ImageArtifact(path="image.png", mime_type=ImageMimeType.PNG)
```

Relevant source:

- `src/celeste/artifacts.py`
- `src/celeste/mime_types.py`
- `references/verification.md` for focused test selection

## Messages And Tools

Use `Message` and `Role` for conversation structures. `Message.content` is either plain text or an ordered `list[MessagePart]`.

For native multimodal chat input, wrap media artifacts in message parts:

```python
from celeste import ImagePart, Message, Role, TextPart
from celeste.artifacts import ImageArtifact

message = Message(
    role=Role.USER,
    content=[
        TextPart(text="Describe this image"),
        ImagePart(image=ImageArtifact(path="image.png")),
    ],
)
```

Do not pass raw artifacts, mixed raw lists, or structured Pydantic payloads directly as `Message.content`. Structured tool payloads belong in `ToolResult.content`, and `ToolResult` is a separate message-list item, not a `Message` subclass.

Use `tools=[WebSearch()]`, `tools=[XSearch()]`, or `tools=[CodeExecution()]` for provider tools.

Tool choice uses `ToolChoice.AUTO`, `ToolChoice.REQUIRED`, or `ToolChoice.NONE`.

Relevant source:

- `src/celeste/types.py`
- `src/celeste/messages.py`
- `src/celeste/tools.py`
- `references/verification.md` for focused test selection

## Structured Outputs

Pass a Pydantic model class through `output_schema`.

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

model_id = "..."  # choose from celeste.list_models(...)

response = await celeste.text.generate(
    "Extract user info: John is 30",
    model=model_id,
    output_schema=User,
)
user = response.content
```

Check provider-specific structured output behavior before changing SDK internals:

- `src/celeste/structured_outputs.py`
- `src/celeste/protocols/openresponses/parameters.py`
- `src/celeste/protocols/chatcompletions/parameters.py`
- provider-specific parameter mapper files
- `references/verification.md` for focused test selection

If notes such as `common_agent_mistakes.md` mention provider-specific structured-output constraints, verify the constraint against current source, tests, or provider behavior before enforcing it. Scope any warning to the affected provider and request path.
