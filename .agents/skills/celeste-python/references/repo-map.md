# Celeste Repo Map

Use this map first when working with Celeste. It is an orientation layer, not a substitute for reading the current source before editing.

## Public Surface

Primary app-facing imports are exported from `src/celeste/__init__.py`.

Use domain namespaces for normal app code:

- `celeste.text.generate(...)`
- `celeste.text.embed(...)`
- `celeste.images.generate(...)`
- `celeste.images.edit(...)`
- `celeste.images.analyze(...)`
- `celeste.images.embed(...)`
- `celeste.audio.speak(...)`
- `celeste.audio.analyze(...)`
- `celeste.audio.embed(...)`
- `celeste.videos.generate(...)`
- `celeste.videos.analyze(...)`
- `celeste.videos.embed(...)`
- `celeste.documents.analyze(...)`

Namespace implementations live in `src/celeste/namespaces/domains.py`. They route domain operations to modality clients through `create_client(...)`.

Use `create_client(...)` when code needs explicit client reuse or lower-level control over:

- `modality`
- `operation`
- `provider`
- `model`
- `protocol`
- `base_url`
- `api_key` or `auth`

Model discovery lives in `src/celeste/models.py`:

- `list_models(provider=..., modality=..., operation=...)`
- `get_model(model_id, provider=...)`
- `register_models(...)` for SDK registry work

App integrations should normally consume model discovery rather than creating local model catalogs.

## Core Concepts

Core enums live in `src/celeste/core.py`:

- `Provider`: backend vendor or local provider.
- `Protocol`: wire-compatible API format such as `openresponses` or `chatcompletions`.
- `Modality`: output/client family such as text, images, videos, audio, embeddings.
- `Operation`: action such as generate, edit, analyze, speak, transcribe, embed, upscale.
- `Domain`: resource the user works with, used by namespace routing.
- `InputType`: optional media input categories.
- `Parameter`: common parameter names shared across modalities.
- `UsageField`: normalized usage keys.

I/O and content types:

- `src/celeste/io.py`: `Input`, `Output`, `Chunk`, `Usage`, `FinishReason`, input-type inference.
- `src/celeste/types.py`: `Message`, `Role`, `MessageContent`, `MessagePart`, `TextPart`, `ImagePart`, `AudioPart`, `VideoPart`, `DocumentPart`, `TextContent`, `ToolResultContent`, media content aliases.
- `src/celeste/messages.py`: canonical chat-message helpers for request-message construction, content-part normalization, media detection, tool-result serialization, and provider part support checks.
- `src/celeste/artifacts.py`: `Artifact`, `ImageArtifact`, `VideoArtifact`, `AudioArtifact`, `DocumentArtifact`.
- `src/celeste/mime_types.py`: MIME `StrEnum`s such as `ImageMimeType.PNG`.
- `src/celeste/tools.py`: `Tool`, `WebSearch`, `XSearch`, `CodeExecution`, `ToolChoice`, `ToolResult`, `ToolOutput`, `ToolError`.

Prefer these types over app-local strings or duplicate models.

## Runtime Layering

The core client layering is in `src/celeste/client.py`:

```text
HTTPClient
  ^
APIMixin
  ^
ModalityClient
  ^
Concrete provider/modality client
```

`APIMixin` owns provider API behavior such as request transport, URL building, response parsing, and usage mapping. `ModalityClient` owns modality behavior such as `_predict`, `_stream`, parameter mapping, output construction, metadata, warnings for unsupported parameters, and common error handling.

Modality clients live under:

- `src/celeste/modalities/text/client.py`
- `src/celeste/modalities/images/client.py`
- `src/celeste/modalities/audio/client.py`
- `src/celeste/modalities/videos/client.py`
- `src/celeste/modalities/embeddings/client.py`

They expose operations and sync/stream namespaces. Examples:

- text: `generate`, `analyze`, `stream.generate`, `sync.generate`
- images: `generate`, `edit`, `stream.generate`, `sync.edit`
- audio: `speak`, `stream.speak`, `sync.speak`
- videos: `generate`, `edit`, `sync.generate`
- embeddings: `embed`, `sync.embed`

## Provider And Modality Registration

Provider support has multiple seams. Do not collapse them into one invented registry.
Directory presence alone is not active provider support. A provider is active only when its enum, auth registration, provider API or protocol seam, modality client/map, model aggregation, and tests are wired.

Provider auth registration:

- `src/celeste/providers/<provider>/__init__.py`
- registers credentials with `register_auth(...)`
- examples: OpenAI, Anthropic, Google, Ollama

Provider API mixins:

- `src/celeste/providers/<provider>/<api>/client.py`
- implement provider wire details such as `_make_request`, `_make_stream_request`, `_parse_usage`, `_parse_content`, `_parse_finish_reason`
- examples: `providers/openai/responses`, `providers/google/generate_content`, `providers/byteplus/videos`

Protocol clients:

- `src/celeste/protocols/openresponses/*`
- `src/celeste/protocols/chatcompletions/*`
- shared wire mixins, streaming parsers, tool mappers, and base parameter mappers for compatible APIs
- text-specific protocol clients live in `src/celeste/modalities/text/protocols/*` and are the concrete clients registered for `create_client(protocol=...)`
- compatible `protocol=` / `base_url` client support is currently text-only

Modality-specific provider clients:

- `src/celeste/modalities/<modality>/providers/<provider>/client.py`
- combine provider API mixins with modality clients
- define provider-specific `parameter_mappers`
- adapt parsed provider content into modality outputs

Modality provider maps:

- `src/celeste/modalities/<modality>/providers/__init__.py`
- maps `Provider` enum values to modality client classes
- feeds `_CLIENT_MAP` in `src/celeste/__init__.py`

Model aggregation:

- `src/celeste/modalities/<modality>/models.py`
- imports provider model lists and exports one modality-level `MODELS`
- `_models` is populated during `celeste` import from these lists

Per-provider model definitions:

- `src/celeste/modalities/<modality>/providers/<provider>/models.py`
- define `Model(id=..., provider=..., display_name=..., operations=..., parameter_constraints=..., streaming=...)`

## Parameter And Constraint System

Universal mapper primitives live in `src/celeste/parameters.py`:

- `Parameters`: base `TypedDict`.
- `ParameterMapper`: maps a unified parameter into provider request shape and can transform output.
- `FieldMapper`: simple direct field mapping.

Common parameter names live in `src/celeste/core.py` as `Parameter`. Modality-specific names live in each modality enum. Model constraints may use either common `Parameter.*` values such as `Parameter.TEMPERATURE` or modality-specific values such as `TextParameter.OUTPUT_SCHEMA`.

Modality parameter names and `TypedDict`s live under:

- `src/celeste/modalities/text/parameters.py`
- `src/celeste/modalities/images/parameters.py`
- `src/celeste/modalities/audio/parameters.py`
- `src/celeste/modalities/videos/parameters.py`
- `src/celeste/modalities/embeddings/parameters.py`

Provider-specific mappers live under both protocol and modality provider packages. Examples:

- `src/celeste/protocols/openresponses/parameters.py`
- `src/celeste/protocols/chatcompletions/parameters.py`
- `src/celeste/modalities/text/providers/google/parameters.py`
- `src/celeste/modalities/images/providers/openai/parameters.py`

Model support for parameters comes from `Model.parameter_constraints`, not from a separate allowlist. Constraints live in `src/celeste/constraints.py` and include:

- `Choice`
- `Range`
- `Pattern`
- `Schema`
- media constraints such as `ImageConstraint`, `ImagesConstraint`, `DocumentConstraint`
- tool constraints such as `ToolSupport`, `ToolChoiceSupport`

Optional input support is inferred from constraints through `src/celeste/io.py`.

## Templates

Start new provider, protocol, modality, and test work from templates:

- `templates/providers/{provider_slug}/`
- `templates/providers/{provider_slug}/{api_slug}/`
- `templates/modalities/{modality_slug}/`
- `templates/modalities/{modality_slug}/providers/{provider_slug}/`
- `templates/protocols/{protocol_slug}/`

## Tests As Executable Documentation

Use focused tests by seam. The canonical test routing matrix lives in `references/verification.md`; keep detailed test-file lists there to avoid duplicate drift.

Common commands:

- `make lint`
- `make typecheck`
- `make test`
- focused tests with `uv run pytest tests/unit_tests/<file>.py -q`

`make format` and current `make ci` may rewrite files; use them only when mutation is intended.

## Source-Of-Truth Order

When sources disagree, follow this order:

1. Current source code in `src/celeste/`.
2. Current tests and templates for existing behavior.
3. README examples and public exports.
4. OpenSpec artifacts for the active change's intended behavior and acceptance criteria.
5. Notes such as `common_agent_mistakes.md`.
6. Model memory.

`common_agent_mistakes.md` is advisory. Keep useful warnings, but verify every rule against current code and task context.
