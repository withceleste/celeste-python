# Templates

Copy the template, replace the `{placeholders}`, strip the `.template` extension. Never write provider or modality files from scratch.

## Which route

1. **New provider with its own wire API** — copy `providers/{provider_slug}/{api_slug}/` (wire mixin: HTTP + parsing, mappers with no `.name`) and `modalities/{modality_slug}/providers/{provider_slug}/` (composite client, `.name`-bound mappers, model catalog). Checklist: CONTRIBUTING.md "Adding a provider".
2. **Provider speaks an existing protocol** (`chatcompletions`, `openresponses`) — subclass the shared clients in `src/celeste/protocols/` via `templates/protocols/`; do not copy the provider templates. A protocol is a wire format served by many vendors.
3. **Second wire API on an existing provider** — copy only `providers/{provider_slug}/{api_slug}/` (including `__init__.py`). On the modality side: demote the existing `client.py` to `{old_api}.py` (classes renamed `{Provider}{Api}{Modality}Client`), give every mapper set in `parameters.py` its backend token (see Naming), add `{new_api}.py` with the same shape, and make `client.py` the dispatcher from `modalities/{modality_slug}/providers/{provider_slug}/_dispatcher.py.template`. Enum, auth, exports, and the `PROVIDERS` registry entry stay untouched. Checklist: CONTRIBUTING.md "Adding a second API to an existing provider".

## Naming

| Thing | Name | Example |
|---|---|---|
| Wire mixin (`providers/`) | `{Provider}{Api}Client` | `GoogleInteractionsClient` |
| Registered modality client | `{Provider}{Modality}Client` | `GoogleTextClient` |
| Per-backend modality client | `{Provider}{Api}{Modality}Client` | `GoogleInteractionsTextClient` |
| Wire-mixin import (composition side) | `{Provider}{Api}Client as {Provider}{Api}Mixin` — always, collision or not | `CohereChatClient as CohereChatMixin` |
| Wire-stream import (composition side) | `{Provider}{Api}Stream as _{Provider}{Api}Stream` — always | `CohereChatStream as _CohereChatStream` |
| Wire config import | plain `from celeste.providers.{provider}.{api} import config` — never aliased | — |
| Mapper set, single-backend file | bare classes + one `{PROVIDER}_PARAMETER_MAPPERS` | `TemperatureMapper`, `COHERE_PARAMETER_MAPPERS` |
| Mapper set, multi-backend file | every set tokened: `{Backend}NameMapper` classes, `_{Backend}NameMapper` wire aliases, `{PROVIDER}_{BACKEND}_PARAMETER_MAPPERS` lists — no bare set survives | `VertexTemperatureMapper`, `GOOGLE_VERTEX_PARAMETER_MAPPERS` |
| Module functions, multi-backend file | backend-token suffix on every function | `map_grounding_vertex`, `map_grounding_interactions` |
| Public module-level data constants | `{PROVIDER}_...`; `MODELS` is the sole bare contract name | `GOOGLE_VOICES`, `GOOGLE_SUPPORTED_MIME_TYPES` |

The prefix is always the `Provider` enum name, never a brand or model family (`Google`, not `Gemini`). A family token may follow the provider prefix only when parallel same-kind constants partition the data (`GOOGLE_IMAGEN_MODELS` / `GOOGLE_GEMINI_MODELS`). The backend token is the backend file name (`imagen.py` → `Imagen`, `vertex.py` → `Vertex`, `interactions.py` → `Interactions`). Wire helper functions, protocol base clients, and module-private names (`_IMAGEN_MODEL_IDS`) keep their real names.

## Notes

- The commented Vertex block in `providers/{provider_slug}/{api_slug}/client.py.template` is only for providers that serve the SAME wire API on both api-key and ADC auth (different host). A different wire format per auth is route 3, not a `_build_url` branch.
- When a modality stream needs events the base `_parse_chunk` filtering drops (tool calls, thought signatures), retain them: seed a private list in `__init__`, append in `_parse_chunk` before calling `super()`, and return it from the matching `_aggregate_*` hook (see the anthropic and google streams).
