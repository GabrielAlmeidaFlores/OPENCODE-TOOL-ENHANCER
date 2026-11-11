---
name: api-contract
description: Design or change HTTP/RPC contracts safely. Use when adding endpoints, changing payloads, or evolving public interfaces.
---

# API Contract

## Before changing

- Identify every consumer: local code, tests, generated clients, external callers.
- Decide whether the change is additive, deprecating, or breaking.
- Prefer additive fields and new versions over in-place breaking changes.

## Checklist

- **Naming** — consistent with existing resources and casing.
- **Status codes** — correct semantics; no 200 with an error body.
- **Errors** — stable machine-readable code, human message, request ID.
- **Validation** — reject invalid input at the boundary with a useful message.
- **Pagination** — explicit cursor or offset; stable ordering.
- **Idempotency** — safe retries for creates and payments.
- **Timeouts** — documented upstream timeout and retry policy.
- **Auth** — object-level authorization, not only route-level.
- **Versioning** — documented strategy and deprecation window.
- **Docs** — update the OpenAPI/RPC schema and examples.

## Output

Return the contract diff, the compatibility verdict, and the migration path for consumers. Do not implement until the verdict is accepted.
