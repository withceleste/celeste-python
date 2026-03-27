# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

---

## [0.11.0] - 2026-03-27

55+ PRs merged, 400+ files changed.

## 1. Tool Calling (v0.11.0 — headline)

Unified tool calling across all providers — the bridge between LLM reasoning and real-world action.

- Single `tools=` parameter replaces `web_search=True`, `x_search=True`, `code_execution=True`.
- **Three tool shapes:**
  - **Built-in tools** (server-side, provider-mapped): `WebSearch(blocked_domains=["reddit.com"])`, `XSearch()`, `CodeExecution()`
  - **User-defined function tools** (dict with `name` + `parameters`): `{"name": "get_weather", "parameters": WeatherParams}`
  - **Raw passthrough** (dict without `name`): `{"type": "bash_20250124"}` — escape hatch for provider-specific tools
- **New types:** `Tool`, `WebSearch`, `XSearch`, `CodeExecution`, `ToolCall`, `ToolResult`, `ToolDefinition`
- **Multi-turn tool use** via `ToolResult(Message)` — tool results are messages in the conversation array.
- **Streaming tool calls** — tool call deltas accumulate during streaming, reconstructed into `ToolCall` objects after stream exhaustion.
- **Architecture:** `ToolMapper` per tool type per provider (parallel to `ParameterMapper`). `ToolsMapper` dispatches by tool type. `ToolSupport` constraint on models declares which built-in tools are supported.
- **Deprecated param shims** — `web_search=True` still works with `DeprecationWarning`, removal date 2026-06-07.
- **Philosophy:** Celeste is primitives, not a framework. Tools are a parameter — celeste passes schemas to providers, normalizes responses into `ToolCall` objects, and returns them. It never auto-executes.
- PRs: #199, #228, #229, #232, #234, #235
- Files: `src/celeste/tools.py` (new), provider `tools.py` files (6 new), `tests/integration_tests/text/test_tools.py` (new)

## 2. Protocol Layer (v0.10.0)

Extracted shared protocol implementations from provider-specific code. Providers now inherit protocol base classes and override only what differs.

- **ChatCompletions protocol** (`protocols/chatcompletions/`) — shared `/v1/chat/completions` implementation. Used by: DeepSeek, Groq, HuggingFace, Mistral, Moonshot.
- **OpenResponses protocol** (`protocols/openresponses/`) — shared Responses API implementation. Used by: OpenAI, xAI, Ollama.
- **`protocol=` + `base_url=` parameters** (v0.11.0, #241) — connect to any compatible API (vLLM, Ollama, MiniMax, LocalAI) without a registered provider. Protocol is wire format identity, not company name.
- **~2000 lines of provider code deduplicated** across 34 files. Provider clients went from ~140 lines to ~10-30 lines.
- Each protocol provides: `client.py`, `config.py`, `parameters.py`, `streaming.py`, `tools.py`.
- PRs: #153, #154, #241
- Files: `src/celeste/protocols/` (new directory)

## 3. Vertex AI (v0.10.0)

Route requests through Google Vertex AI for any supported provider.

- `GoogleADC` auth with `project_id` and `location` fields.
- All Google providers routable through Vertex AI (text, images, embeddings, video, TTS).
- Cross-provider support: Anthropic, Mistral, and DeepSeek on Vertex AI.
- `_make_poll_request` for long-running operations (video generation).
- `google-auth` moved to optional `[gcp]` extra (#133) — saves ~24.5 MB for non-GCP users.
- 39 unit tests for URL routing in `test_vertex_routing.py`.
- PR: #135
- Files: `src/celeste/auth.py`, all provider clients

## 4. New Providers

- **HuggingFace** (v0.10.2, #183) — OpenAI-compatible inference router (`router.huggingface.co`), 127+ models across 15 inference providers. Uses ChatCompletions protocol. Credential: `HF_TOKEN`.
- **xAI Grok Imagine** (v0.9.6, #128) — Image generation (`grok-imagine-image`) and video generation (`grok-imagine-video`) with aspect ratios, num_images, duration, resolution. Async polling for video.
- **Ollama Images** (v0.9.4, #119) — Local image generation via `/api/generate`. Flexible parameter validation (pass-through for dynamic providers). Adds `NEGATIVE_PROMPT` parameter.
- **OpenResponses + Ollama Text** (v0.9.4, #111) — `Provider.OPENRESPONSES` for Responses-compatible APIs, `Provider.OLLAMA` for local inference. `NoAuth` for local providers, `base_url=` for custom gateways.
- Files: `src/celeste/providers/huggingface/`, `src/celeste/providers/xai/images/`, `src/celeste/providers/xai/videos/`, `src/celeste/providers/ollama/`

## 5. New Models

**Anthropic:**
- Claude Opus 4.6 (#130) — 64K max tokens, 32K thinking budget
- Claude Sonnet 4.6 (#179) — 64K max tokens, extended thinking

**Google:**
- Gemini 3.1 Pro Preview (#179) — thinking levels: low/medium/high
- Gemini 3.1 Flash Lite Preview (#213)

**OpenAI:**
- GPT-5.4, GPT-5.4 Pro (#213) — thinking budget + verbosity

**xAI:**
- Grok 4.20 Beta (reasoning + non-reasoning) (#213)

**BytePlus:**
- Seedream 5.0 Lite (#181) — 2K/3K quality tiers, 16 resolution presets

**Moonshot:**
- Kimi K2.5 — with WebSearch tool support

**Removed (no longer available on provider APIs, #243):**
- OpenAI: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
- xAI: Grok 2 Vision 1212
- Groq: Llama 4 Maverick 17B 128E

## 6. Multi-turn Conversations (v0.9.4)

First-class support for multi-turn conversations across all text providers.

- `Message(role, content, tool_calls)` and `Role` (USER, ASSISTANT, SYSTEM, DEVELOPER) types.
- All text entrypoints accept `messages=` parameter for conversation history.
- Provider normalization: Anthropic system messages extracted to top-level, Google system_instruction, chat vs responses arrays.
- PR: #111
- Files: `src/celeste/types.py`, all text provider clients

## 7. Breaking Changes

- **`web_search=`/`x_search=`/`code_execution=` deprecated** — replaced by `tools=[WebSearch()]`. Old boolean params work via shims with `DeprecationWarning` until 2026-06-07.
- **`google-auth` moved to optional extra** (#133) — `pip install "celeste-ai[gcp]"` required for Vertex AI. Raises `MissingDependencyError` with install instructions if missing.
- **`requests` removed from runtime deps** (#132) — only needed as `google-auth[requests]` transport.
- **Deprecated models removed** (#243) — GPT-4, GPT-4 Turbo, GPT-3.5 Turbo, Grok 2 Vision 1212, Llama 4 Maverick (all dead on provider APIs).
- **`_parse_content` signature change** (#203) — now `(self, response_data) -> Content`, no `**parameters`. Affects custom provider subclasses.
- **`FieldMapper.name` type change** (#161) — from `StrEnum` to `ClassVar[StrEnum]`. Affects custom `ParameterMapper` subclasses.
- **`ModalityClient` constructor** (#241) — gained `protocol=` and `base_url=`; `provider` became `Provider | None`.

## 8. Bug Fixes

- **BlockingPortal thread leak** (#239) — sync stream iteration leaked portal thread on exception, `break`, or abandonment. Rewrote `__iter__` as generator with `try/finally` for guaranteed cleanup. Fixed CI hanging 19 minutes after tests.
- **SSE stream error detection** (#192) — mid-stream errors (Anthropic `overloaded_error`, OpenAI `server_error`) now raise `StreamEventError` instead of being silently discarded.
- **Streaming HTTP error enrichment** (#196) — consistent provider-enriched error messages across streaming and non-streaming paths.
- **`json.loads` strict mode** (#152) — LLM-generated content with literal `\n` in thinking fields caused `Invalid control character` errors. Fixed with `strict=False` in all 8 provider `parse_output` methods.
- **`UnicodeDecodeError` in error handler** (#171) — binary error bodies (e.g. `0xff`) escaped the catch block.
- **`_parse_usage` return type mismatch** (#174) — 3 modality-level overrides returned typed objects instead of `RawUsage` dicts, crashing on Gemini/Imagen.
- **Streaming image edits routed to wrong endpoint** (#180) — OpenAI streaming edits sent to `/v1/images/generations` instead of `/v1/images/edits`.
- **Empty/whitespace credentials** (#190) — now raises `MissingCredentialsError` instead of sending empty API keys.
- **API key whitespace causing HTTP errors** (#116) — strip whitespace from API keys to prevent `LocalProtocolError: Illegal header value`.
- **Null `tool_calls` in ChatCompletions streaming** — DeepSeek sends `"tool_calls": null` instead of omitting the key. `.get("tool_calls", [])` returns `None` when key exists with null value. Fixed with `or []`.
- **Pydantic V2.11 deprecation** — `tool.model_fields` on instance changed to `type(tool).model_fields` (class access) in 4 tool mapper files.

## 9. DX Improvements

- **`extra_body=` on all modalities** (#126) — pass provider-specific fields into the request body on images, audio, videos, embeddings.
- **`extra_headers=` on all client methods** (#193) — `generate`, `stream`, `analyze`, `speak`, `embed`, `edit` all accept `extra_headers: dict[str, str] | None`.
- **`auth=` passthrough on all namespace methods** (#146) — previously only async text generation passed it through, silently dropping it elsewhere. Vertex AI auth now works across all domains.
- **`UnsupportedParameterWarning`** (#212) — warns when parameters are silently ignored by a provider instead of failing silently.
- **`InvalidToolError`** (#228) — immediate error for bad tool list items (e.g., `tools=[WebSearch]` without `()`, strings, integers).
- **WebSearch config field drop warnings** (#235) — warns when fields like `blocked_domains` or `max_uses` aren't supported by the provider.
- **Base64 serialization** (#145) — `ser_json_bytes="base64"` on Output/Chunk models ensures `model_dump_json()` correctly base64-encodes artifact data.
- **Colab quickstart notebook** (#115) — `notebooks/celeste-colab-quickstart.ipynb`.
- **CONTRIBUTING.md rewrite** (#131) — accurate workflow documentation.

## 10. Architecture (Internal)

- **FieldMapper base class** (#161) — replaces repeated validate-then-set pattern across 45 mapper classes with 2-line declarations.
- **`_content_fields` ClassVar** (#160) — replaces 20 identical `_build_metadata()` overrides with one-line declarations. -215 lines.
- **Generic `MediaConstraint`** (#176) — 6 near-identical media constraint classes (~190 lines) replaced with two generic bases.
- **Stream base class consolidation** (#168, #172) — `_parse_chunk_content`/`_wrap_chunk_content` hooks. 6 text provider streams became empty classes. -521 lines total.
- **`ParameterMapper` generic on Content** (#189) — PEP 695 generics, end-to-end type safety.
- **`_transform_output` moved to base `_predict`** (#187) — prevents silent structured output failures in new providers.
- **`_json_headers()` helper** (#162) — replaces verbatim auth + Content-Type header construction across every provider client.
- **Artifact validator handles base64** (#139) — removed manual `base64.b64decode()` across 6 provider clients.
- **ChatCompletionsTextClient protocol base** (#199) — modality-level protocol class that DeepSeek, Groq, HuggingFace, Mistral, Moonshot inherit from.
- **Provider-level OpenResponses removed** (#229) — OpenAI/xAI/Ollama now use protocol-level `OpenResponsesTextClient`. -396 lines.

## 11. Testing

- **+882 lines of new tests** across unit and integration suites.
- Integration tests for tools: 17 parametrized runs across 4 providers (Anthropic, OpenAI, Google, xAI) — WebSearch, streaming, function tools, XSearch, multi-turn ToolResult round-trip.
- Vertex AI routing tests: 39 tests covering URL routing for all provider/modality combinations.
- Protocol base URL tests: 185 lines (`test_protocol_base_url.py`).
- Streaming tests expanded: +246 lines, sync iteration cleanup tests.
- Exception tests: `InvalidToolError`, `StreamEventError`.
- Client tests: unsupported parameter warnings, deprecated param shims.
- Constraint tests: `ToolSupport` validation (5 tests).
- Test count: ~478 → 527+.

## Contributors

- @Leo-le-jeune — HuggingFace text generation provider (#183)
- @Seluj78 and @Olaiwonismail — CONTRIBUTING.md rewrite (#131)
- @Alistorm and @XinyueZ — design input on the tool calling architecture (#150)

---

## [0.9.1] - 2026-01-17

279 files changed. Monolith rewrite — single package, modality-first architecture.

## Packaging Rationale (Monolith)
- DX first: pip install celeste-ai is the only thing most users want to remember. Requiring extras like celeste-ai[text] adds cognitive load and drops adoption.
- Lightweight anyway: importing modalities/providers doesn’t add “weight” in practice. The package stays tiny (under ~2 MB), and 90% of the code is core no matter what.
- No heavyweight vendor SDKs: Celeste uses lightweight HTTP clients, so “bundling providers” doesn’t drag in massive dependencies.
- Faster + cleaner: removing the registry/entry‑points means fewer indirections, no dynamic discovery, and faster startup with clearer behavior.
- Simpler maintenance: one package, one version, one release pipeline. Fewer moving parts and fewer “what do I install?” support tickets.
- Predictable behavior: providers are always available; no hidden runtime failures because a plugin wasn’t installed.
- Better UX in docs: one install step + one API surface; examples “just work.”

## Packaging Changes
- Removed the legacy multi-package workspace and extras-only install paths.
- Now ships as a single PyPI package (`celeste-ai`).
- Updated dependency and tooling configuration to the monolith layout (tests/coverage/mypy/ruff paths now target `src` and `tests` only).
- File updated: `pyproject.toml`.
- File updated: `Makefile`.
- Files deleted: `packages/` (all legacy capability/provider packages and their tests).

## Tests
- Added modality-first integration tests (`tests/integration_tests/**`) covering generate/edit/analyze/speak and streaming flows per modality.
- Added media fixtures for image/audio/video analysis in integration tests.
- Expanded unit tests for namespace routing, modality inference, stream metadata, auth/credentials registry, artifact handling, and IO validation.
- Replaced legacy package-based tests with a unified monolith test layout.
- Files added: `tests/integration_tests/**`, `tests/testing_guidelines.md`, `tests/unit_tests/utils/**`, `tests/__init__.py`.
- Files updated: `tests/unit_tests/*.py`.
- Files removed: legacy package-specific test suites under `packages/**`.

## CI/CD
- CI workflow now targets monolith paths only (`src/celeste`, `tests`) for ruff, mypy, and bandit.
- Publish workflow runs required integration tests from `tests/integration_tests` and no longer uses package-based change detection.
- Build step produces a single package (`uv build`) before TestPyPI → PyPI → GitHub release.
- Files updated: `.github/workflows/ci.yml`, `.github/workflows/publish.yml`.

## Feature Highlight: `extra_body` passthrough
- New `extra_body` parameter lets you pass provider-specific fields or arbitrary JSON into the request body.
- This unblocks new provider capabilities before Celeste adds first-class parameter mapping.
- Implemented via deep-merge into the built request payload.
- File updated: `src/celeste/client.py`.

## Architecture Shift: Modalities
- v1 moves from capability-centric clients (one method) to modality-centric clients (one output type). Modality = output type (text/images/audio/video/embeddings), operations become methods (`generate`, `edit`, `analyze`, `embed`).
- Domain is the resource you work with (e.g., videos), regardless of whether the input is text or media; modality is what comes out (output type). This clarifies why one client can expose multiple operations while still being type-safe.
- Namespaces are domain-first (the resource you work with); `create_client` is modality-first (the output type you want). Routing uses (domain, operation) → modality.
- Cross-domain operations are explicit: image/audio/video analysis always routes to the text modality; embeddings always route to the embeddings modality.
- Operations exposed: text `generate`/`embed`, images `generate`/`edit`/`analyze`, audio `speak`/`analyze`, videos `generate`/`analyze`.
- Files added: `src/celeste/modalities/` (text/images/audio/videos/embeddings submodules).

## Namespace API
- Domain namespaces (`celeste.text`, `celeste.images`, `celeste.audio`, `celeste.videos`) provide one-line calls that route to the correct modality/operation under the hood.
- Domain indicates the resource you work with, even if the input is different (e.g., video generation can take text input but stays in the videos domain). Modality indicates the output type (e.g., `celeste.images.analyze(...)` routes to the text modality because analysis returns text).
- The namespace pattern is more discoverable (IDE autocomplete) and matches how people think: start from the domain, then pick the action.
- Execution modes are explicit via namespace properties: async by default, with `.sync` and `.stream` for blocking and streaming workflows.
- The factory pattern remains available for explicit configuration and client reuse when you want full control.
- Files added: `src/celeste/namespaces/__init__.py`, `src/celeste/namespaces/domains.py`.

## Providers
- Added monolith provider layer under `src/celeste/providers/` with per-provider config/parameters/streaming modules.
- Provider modules include: OpenAI (responses/images/audio/videos), Google (generate_content/imagen/veo/cloud_tts/embeddings/interactions), Anthropic (messages), Cohere/Mistral/DeepSeek/Groq/Moonshot (chat), xAI (responses), ElevenLabs/Gradium (text_to_speech), BFL/BytePlus (images + videos).
- Central provider exports in `providers/__init__.py` for import/discovery.
- Added provider API references doc at `src/celeste/providers/api_references.md`.
- Files added: `src/celeste/providers/**` and `src/celeste/providers/__init__.py`.

## Contributor Templates
- Added code generation templates for contributors to easily add new modalities, providers, or parameters.
- Templates follow the monolithic architecture with proper relative imports and type patterns.
- **Modality templates** (`templates/modalities/`): Full scaffolding for new output types including client, IO types, parameters, streaming, provider implementations, and integration tests.
- **Provider API templates** (`templates/providers/`): Scaffolding for new provider HTTP clients including config, client mixin, streaming, and parameter mappers.
- Templates include: `client.py`, `io.py`, `parameters.py`, `streaming.py`, `models.py`, `config.py`, and test files.
- Placeholder conventions: `{Modality}` (PascalCase), `{modality}` (lowercase), `{Provider}`, `{provider}`, `{Api}`, `{api}`, `{Content}`.
- Files added: `templates/modalities/**`, `templates/providers/**`.

## API Wiring
- Updated public exports to v1 surface, including modalities, operations, clients, structured outputs, and namespace singletons.
- Added modality/provider client map and auto-registered modality models at import time.
- Added capability-to-(modality, operation) translation layer to keep `capability` supported with a deprecation warning.
- `create_client` now supports modality + operation arguments, infers operations when possible, and resolves models with better modality-aware errors.
- File updated: `src/celeste/__init__.py`.

## Docs
- Updated Quick Start and multimodal examples to the namespace‑first v1 API.
- Added a Namespace API section and an “Advanced: create_client” section.
- Added “Behavior changes since v0.3.9”.
- Replaced extras installs with a single‑package install (`pip install celeste-ai` / `uv add celeste-ai`).
- Updated the PyPI badge and added the v1 beta callout banner.
- File updated: `README.md`.

## Release Prep
- Set package version to `0.9.1` for the public v1 beta.
- Updated development status classifier to Beta.
- Removed notebook/scraping-only runtime deps from install requirements (ipykernel, matplotlib, beautifulsoup4).
- File updated: `pyproject.toml`.


## Client Core / Modality Architecture (`src/celeste/client.py`)
- Replaced the capability-specific `Client` with a unified `ModalityClient` base class.
- Removed the capability/provider client registry and related lookup helpers.
- Added `modality` as a first-class field and use it for HTTP client selection.
- Added `sync` and `stream` namespace properties for modality clients.
- `_predict` now takes explicit `inputs` plus optional `endpoint` and `extra_body`, and expects provider `_make_request` to return a response data dict (not an `httpx.Response`).
- `_stream` now takes explicit `inputs` and a `stream_class`, passes `client=self`, and supports `extra_body` + `streaming=True`.
- Added `APIMixin._deep_merge` and extended `_build_request` to merge `extra_body` into the request body.
- Removed capability compatibility validation at init time.
- Updated content types to `TextContent` / generic `Content` and adjusted `_transform_output` accordingly.
- Metadata now includes `modality` and the raw response payload.
- File updated: `src/celeste/client.py`.

## Auth + Credentials (`src/celeste/auth.py`, `src/celeste/credentials.py`)
- Renamed `APIKey` to `AuthHeader` (with `secret`, `header`, `prefix`), keeping `APIKey` as a backwards-compatible alias.
- `get_auth_class` no longer auto-loads providers from entry points; auth types must be registered explicitly.
- Replaced static provider maps with dynamic auth registry (`register_auth`, `get_auth_config`).
- Added credential fields for `MOONSHOT_API_KEY`, `DEEPSEEK_API_KEY`, and `GROQ_API_KEY`.
- `get_auth` now instantiates custom auth classes or builds an `AuthHeader` from the registry.
- `has_credential` returns true for auth-class providers; `list_available_providers` now filters by registry + credentials.
- Files updated: `src/celeste/auth.py`, `src/celeste/credentials.py`.

## Artifacts + MIME (`src/celeste/artifacts.py`, `src/celeste/mime_types.py`)
- Added `get_bytes()` and `get_base64()` primitives for content access.
- Removed `_default_mime_type` and `to_data_url()` (moved to utilities).
- Added `src/celeste/utils/mime.py` with `detect_mime_type()` and `build_image_data_url()`.
- MIME detection uses `filetype` library (magic bytes).
- Added JSON serialization for `data: bytes` using base64.
- Files updated: `src/celeste/artifacts.py`, `src/celeste/mime_types.py`.
- Files added: `src/celeste/utils/`.

## HTTP + WebSocket (`src/celeste/http.py`, `src/celeste/websocket.py`)
- Switched shared client registries to use `Modality` instead of `Capability`.
- HTTP client now recreates the `httpx.AsyncClient` if the event loop changes to avoid "Event loop is closed" errors.
- Files updated: `src/celeste/http.py`, `src/celeste/websocket.py`.

## Streaming (`src/celeste/streaming.py`)
- Added sync iteration support via anyio blocking portals (`__iter__`, `__next__`).
- Added sync context manager support (`__enter__`, `__exit__`) with portal cleanup.
- Added `_build_stream_metadata` hook (default: raw events).
- Stream exhaustion no longer raises `StreamEmptyError` when no chunks were produced.
- Improved cleanup: guard `aclose` during active iteration and suppress close-time runtime errors.
- File updated: `src/celeste/streaming.py`.

## Exceptions (`src/celeste/exceptions.py`)
- `ModelNotFoundError` now supports modality-based messages.
- `ClientNotFoundError` expanded to include modality + operation.
- Added `ModalityNotFoundError`.
- File updated: `src/celeste/exceptions.py`.

## Behavior Changes / Notes
- Provider `_make_request` now returns a response data dict; error handling is expected inside provider implementations.
- Empty streams no longer raise `StreamEmptyError` on exhaustion.
- Auth types are no longer auto-loaded from entry points; they must be registered explicitly.
- Related files: `src/celeste/client.py`, `src/celeste/streaming.py`, `src/celeste/artifacts.py`, `src/celeste/auth.py`.

---

[Unreleased]: https://github.com/withceleste/celeste-python/compare/v0.11.0...HEAD
[0.11.0]: https://github.com/withceleste/celeste-python/compare/v0.9.1...v0.11.0
[0.9.1]: https://github.com/withceleste/celeste-python/compare/v0.3.9...v0.9.1
