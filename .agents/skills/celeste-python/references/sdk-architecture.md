# Celeste SDK Architecture Reference

Use this for changes inside `src/celeste`, templates, or Celeste tests.

## Layering

`src/celeste/client.py` defines the base layering:

```text
HTTPClient
  ^
APIMixin
  ^
ModalityClient
  ^
Concrete provider/modality client
```

Provider API mixins handle wire details. Modality clients handle operation methods, common prediction/streaming flow, output construction, parameter mapping, metadata, and warnings.

## Public Client Resolution

`src/celeste/__init__.py` builds `_CLIENT_MAP` from modality provider maps and protocol clients.

`create_client(...)` resolves:

- deprecated `capability` into `modality` + `operation`
- model objects or string model IDs
- provider or protocol target
- provider credentials or BYOA protocol auth

When changing client resolution, inspect:

- `src/celeste/__init__.py`
- `references/verification.md` for focused test selection

## Modality Clients

Modality clients define operation-level Python APIs:

- `src/celeste/modalities/text/client.py`
- `src/celeste/modalities/images/client.py`
- `src/celeste/modalities/audio/client.py`
- `src/celeste/modalities/videos/client.py`
- `src/celeste/modalities/embeddings/client.py`

They should delegate request execution through `_predict(...)` and streaming through `_stream(...)`.

## Provider Support Seams

Provider auth registration:

- `src/celeste/providers/<provider>/__init__.py`
- registers credentials or no-auth behavior

Provider API mixin:

- `src/celeste/providers/<provider>/<api>/client.py`
- owns endpoint routing, HTTP request shape, streaming request shape, response parsing, usage mapping, and finish reason parsing

Modality provider client:

- `src/celeste/modalities/<modality>/providers/<provider>/client.py`
- combines the provider API mixin with a modality client
- adapts provider content into `TextContent`, `ImageArtifact`, `AudioArtifact`, `VideoArtifact`, or embeddings
- returns provider-specific stream class where supported

Modality provider map:

- `src/celeste/modalities/<modality>/providers/__init__.py`
- maps `Provider` to concrete modality client class

Model aggregation:

- `src/celeste/modalities/<modality>/models.py`
- imports provider model lists

Per-provider models:

- `src/celeste/modalities/<modality>/providers/<provider>/models.py`
- define `Model` entries with `operations`, `streaming`, and `parameter_constraints`

When adding provider support, check every relevant seam. Missing one seam usually creates runtime lookup or model discovery failures.

## Protocol Clients

Shared compatible API implementations live under:

- `src/celeste/protocols/openresponses/`
- `src/celeste/protocols/chatcompletions/`

These packages own shared wire mixins, streaming parsers, tool mappers, and base parameter mappers.

Concrete text protocol clients live under:

- `src/celeste/modalities/text/protocols/openresponses/`
- `src/celeste/modalities/text/protocols/chatcompletions/`

`create_client(protocol=..., base_url=...)` currently resolves through those text-specific protocol clients. Provider clients can inherit shared protocol behavior instead of duplicating wire behavior when the provider is protocol-compatible.

## Message Serialization

Canonical chat-message helpers live in `src/celeste/messages.py`.

Use those helpers for SDK-internal message work:

- normalize `Message.content` into ordered content parts
- collect media input types from messages and top-level media kwargs
- build request messages from prompt/messages/media inputs
- serialize structured text content for text-only provider fields
- serialize `ToolResult.content` for provider fields that accept JSON objects
- raise clear errors when a provider serializer receives an unsupported message part

Provider and protocol serializers should use these helpers rather than hand-rolled message traversal.

## Parameters And Constraints

Modality parameter enums and `TypedDict`s live under each modality's `parameters.py`.

Provider-specific parameter mapping uses:

- `ParameterMapper`
- `FieldMapper`
- provider/protocol mapper lists such as `OPENRESPONSES_PARAMETER_MAPPERS`, `GOOGLE_PARAMETER_MAPPERS`

Model constraints define supported parameters:

```python
Model(
    id="...",
    provider=Provider.OPENAI,
    operations={Modality.TEXT: {Operation.GENERATE}},
    parameter_constraints={
        TextParameter.OUTPUT_SCHEMA: Schema(),
        TextParameter.TOOLS: ToolSupport(tools=[WebSearch]),
    },
)
```

If adding a parameter, update the relevant modality enum/TypedDict, constraints in model definitions, provider mappers, and tests.

## Artifacts And Media Support

Media support is inferred from model constraints and message content parts. Do not add separate app-side media allowlists.

Relevant source:

- `src/celeste/artifacts.py`
- `src/celeste/mime_types.py`
- `src/celeste/constraints.py`
- `src/celeste/io.py`
- `references/verification.md` for focused test selection

## Streaming

Streaming support requires:

- model `streaming=True`
- provider API `_make_stream_request(...)`
- a stream class for provider/protocol event parsing
- modality stream aggregation when needed

Relevant source:

- `src/celeste/streaming.py`
- modality `streaming.py` files
- protocol/provider streaming files
- `references/verification.md` for focused test selection

## Templates

Use templates before inventing structure:

- `templates/providers/{provider_slug}/`
- `templates/providers/{provider_slug}/{api_slug}/`
- `templates/modalities/{modality_slug}/`
- `templates/modalities/{modality_slug}/providers/{provider_slug}/`
- `templates/protocols/{protocol_slug}/`

Provider API templates are validated by focused tests.
Templates are source of truth for generated provider/module shape. Current source and message helpers are source of truth for multimodal message serialization semantics.

## Tests To Consult

Use `references/verification.md` for the current focused test matrix. Keep detailed test-file routing there to avoid duplicate drift.
