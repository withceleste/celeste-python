# Celeste Python — Recent Diff Summary
Date: 2026-01-15

## Scope
- Source: `git diff` (working tree vs last commit) in `celeste-python`
- Files changed: 279

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
