# Celeste Anti-Patterns

Use this for reviews, debugging, and suspicious Celeste integrations.

## Scope The Rule

Many warnings apply differently depending on context.

App-side integration:

- consume Celeste public APIs
- avoid local duplicates of Celeste concepts
- keep wrappers thin
- prefer `list_models(...)` and existing model discovery

SDK-internal work:

- may update Celeste registries and model definitions
- must follow existing provider/modality/protocol/mapper/test patterns
- should not be blocked by app-side "do not register models" warnings

## Do Not Duplicate Celeste Concepts

Avoid local copies of:

- provider strings when `Provider` applies
- role strings when `Role` applies
- MIME strings when Celeste MIME enums apply
- artifact shapes when `ImageArtifact`, `AudioArtifact`, `VideoArtifact`, or `DocumentArtifact` apply
- message part shapes when `MessageContent`, `MessagePart`, `TextPart`, `ImagePart`, `AudioPart`, `VideoPart`, or `DocumentPart` apply
- model catalogs when `list_models(...)` or existing registry flow applies
- tool result/error wrappers when `ToolOutput` or `ToolError` applies

Local types are fine for truly app-specific transport events or persistence shapes.

## Do Not Bypass Message Semantics

Celeste owns semantic chat message content.

Avoid:

- raw artifacts directly in `Message.content`
- mixed raw lists such as `["text", ImageArtifact(...)]`
- structured Pydantic payloads as normal `Message.content`
- treating `ToolResult` as a `Message` subclass
- hand-rolled provider message serializers in app code or new SDK paths

Use ordered message parts for chat input. Use `ToolResult.content` for structured tool outputs.

## Do Not Invent A Flat Provider Registry

Celeste provider support is intentionally split:

- provider auth registration
- provider enum registration
- provider API mixins
- modality provider maps
- modality-specific provider clients
- per-modality model aggregation
- per-provider model definitions
- parameter mappers and constraints

A new single registry that bypasses these seams is probably wrong.
Directory presence alone is not support; every active provider must be wired through the relevant enum, auth, client, model, map, and test seams.

## Do Not Copy Vendor SDK Shapes Into App Code

Celeste exists to hide provider-specific request/response differences. In app code, avoid OpenAI/Anthropic/Gemini request structures unless the user explicitly asks for provider-specific fallback behavior outside Celeste.

Inside the SDK, provider wire shapes belong in provider API mixins, protocol clients, provider tools, and provider parameter mappers.

## Do Not Add Parameters In Only One Place

New SDK parameters usually need several updates:

- modality parameter enum
- modality `TypedDict`
- model `parameter_constraints`
- provider or protocol mapper
- tests

If only a request-body field was added, the change is probably incomplete.

## Do Not Treat Notes As Canonical

`common_agent_mistakes.md` is useful but not perfect. Verify every warning against:

1. current source
2. current tests/templates
3. public exports and README

Example: app code should not patch Celeste's model registry, but SDK code may legitimately update model definitions or registry behavior.

## Review Checklist

Ask:

- Is this app code or SDK code?
- Is the code using public namespaces where app usage is enough?
- Did it invent local enums or string literals for Celeste-owned concepts?
- Did it duplicate model catalog logic?
- Did it update every provider/modality/model/mapper seam required by the change?
- Did it pick focused tests that match the touched seam?
- Is a warning based on current code, or only on stale memory/notes?
