# Pilot Feature Proposal: Opt-Out of Client-Supplied Request IDs

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** pilot output, structurally verified, not independently reviewed

## Proposal

Add a `trustIncoming?: boolean` option to the `requestId` middleware, defaulting to `true` to preserve existing behavior. When set to `false`, the middleware ignores any incoming request ID header and always uses the configured generator, while still exposing the generated value through `c.get('requestId')` and the response header. This gives applications a straightforward way to prevent clients from choosing their own correlation IDs for logs and tracing without writing a custom generator.

## Acceptance Criteria

1. With the default `trustIncoming: true`, a valid incoming request ID is preserved exactly as today.
2. With `trustIncoming: false`, the generator is called for every request, including requests that contain a syntactically valid incoming ID.
3. With `trustIncoming: false`, `c.get('requestId')` and the response header contain the generated ID, not the incoming one.
4. Existing behavior remains unchanged when `headerName` is an empty string: an ID is still generated, stored, and no header is written.
5. The option is documented in the middleware JSDoc and covered by tests for trusted and untrusted modes.

## Implementation Notes

- The current decision point is the incoming-header lookup followed by the validity and length fallback, which is where the new trust check must gate reuse of client input: `src/middleware/request-id/request-id.ts:48-51`.
- The generated or accepted identifier is already stored in the context and written to the response header in one place, so both must remain consistent after the change: `src/middleware/request-id/request-id.ts:53-56`.
- Adding an optional boolean to `RequestIdOptions` and its destructured defaults is backward-compatible because the new field can default to the current behavior: `src/middleware/request-id/request-id.ts:13-17` and `src/middleware/request-id/request-id.ts:41-45`.
