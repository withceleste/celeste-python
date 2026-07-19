# CLAUDE.md

Celeste: unified multi-modal AI SDK for Python (3.12+, uv). One client API across 20+ providers — text, images, audio, videos, embeddings.

## Core concepts

- **Modality**: the one modality, in addition to text, essential to the model's purpose — the modality the model cannot function without.
- **Domain**: the resource you work with.
- Never describe Modality as an output type or Domain as an input type.
- Key enums, all in `src/celeste/core.py`:
  - `Modality` (text, embeddings, images, videos, audio)
  - `Domain` (text, images, audio, videos, documents)
  - `Operation` — what you do (generate, edit, analyze, speak, transcribe, embed, upscale)
  - `Provider` — which backend serves the request
  - `Protocol` (chatcompletions, openresponses)
- `(Domain, Operation) → Modality` inference: `DOMAIN_OPERATION_TO_MODALITY` in `core.py`.

## Architecture: three layers

1. `src/celeste/providers/<vendor>/<api>/` — wire/HTTP mixins per vendor API.
   - Dirs are named after the API: `anthropic/messages`, `cohere/chat`, `elevenlabs/text_to_speech`.
   - Parameter mapper classes here carry no `.name`.
2. `src/celeste/modalities/<modality>/providers/<vendor>/` — composition layer.
   - `client.py` composes wire mixin + modality client; `parameters.py` binds unified `.name`s; `models.py` is the model catalog.
3. `src/celeste/protocols/` + `src/celeste/modalities/text/protocols/` — shared OpenAI-compatible base clients (`chatcompletions`, `openresponses`).
   - RULE: editing a protocol changes every inheriting vendor (DeepSeek, Moonshot, Groq, Mistral, HuggingFace, ...).
   - Vendor-specific behavior goes in that vendor's override (`client.py` / `parameters.py`), never in the shared base.

Template-first: new files start from `templates/` — `cp` the template, then edit. Never write provider/modality files from scratch. Registration checklist: CONTRIBUTING.md "Adding a provider".

## Model catalog rules (`models.py` entries)

- `Model.streaming` means celeste's adapter transport streams this model — not the vendor's advertised capability. Flip it only after a live call through celeste's own streaming path.
- A `MAX_TOKENS` Range comes only from a provider-documented max-completion/output figure. A context window is never a completion cap; if no completion max is documented, omit the constraint.
- Choice/enum literals verbatim from the provider's API request-parameter reference, not marketing/model pages (those use display tokens). If two official pages conflict, keep the current value and record the conflict.
- One `parameter_constraints` dict serves every call mode (unary AND streaming). Constrain to the union; let the provider reject mode-specific invalids.
- Remove a model id only after a live authenticated call hard-rejects it. Lifecycle/deprecation tables are announcements; providers keep retired aliases serving or silently redirect them.

## Validation philosophy

- A parameter with no constraint passes through to the provider unvalidated — by design (commit d713074).
- Never add local guards, omit-and-warn mappers, or constraints whose only purpose is to reject what the provider already rejects.
- Never encode a mode-conditional restriction (e.g. thinking-mode-only) as an unconditional constraint.

## Workflow

- Implementation starts in a fresh worktree: `git worktree add -b <branch> .worktrees/<name> main`, then `uv sync --all-extras` inside it.
- `make ci` gates every commit (format, lint, typecheck, security, unit tests).
- Integration tests hit real provider APIs (cost money, need keys in `.env`): `make integration-test`.
- One PR per concern: provider-global changes (protocol / transport / `core.py`) never ride in model-addition PRs.
- Never commit or push without explicit maintainer approval.

## Testing

- `make ci` is the gate. House style: wire-contract tests are data-driven over mapper lists (`_map` / `_at` in `tests/unit_tests/test_parameter_wire_contracts.py`); request-payload tests call `client._init_request(...)` directly; stream parse tests instantiate via `object.__new__(...)`; never mock httpx in provider/parameter tests (only `tests/unit_tests/test_http.py` touches the transport).
- A test must earn its place: focused, guarding real behavior, parametrized over cases instead of duplicated. No test ceremony, no coverage bloat. If a test is not clearly required, no test is better than a weak one.

## Transport quirks

- `HTTPClient` (`src/celeste/http.py`) has no query-param support — bake query strings into the URL.
- ElevenLabs binary streaming bypasses `HTTPClient` entirely (raw httpx `client.stream`).
