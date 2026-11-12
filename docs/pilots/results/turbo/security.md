# PILOT_SECURITY — Static Security Triage

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** pilot output, structurally verified, not independently reviewed

**Scope:** Static review of 5 files in the Turborepo CLI auth/API-client path. No tests or dynamic analysis were run. These are triage findings from code inspection, not confirmed exploits.

Files inspected:

- `SECURITY.md`
- `crates/turborepo-auth/src/device_flow.rs`
- `crates/turborepo-auth/src/auth/login.rs`
- `crates/turborepo-auth/src/lib.rs`
- `crates/turborepo-api-client/src/lib.rs`

---

## Risk 1 — SSO token is sent in the URL query string

**Severity: Medium**

`verify_sso_token` issues a `GET` request with the credential as a `token` query parameter:

- `crates/turborepo-api-client/src/lib.rs:308-310` — `GET /registration/verify` plus `.query(&[("token", token.expose()), ("tokenName", token_name)])`.

Tokens in URLs are routinely captured by reverse-proxy access logs, CDN/WAF request logs, browser history, and `Referer` headers. Any log-retention or log-forwarding pipeline for the API tier therefore becomes a credential-retention surface. TLS protects the wire, but not the URL's presence in logs on either end.

**Recommendation:** Send the token in an `Authorization` header (or a POST body) instead of the query string, and scrub any existing logs that may contain `/registration/verify?token=`.

---

## Risk 2 — Preflight response can redirect the bearer token to an arbitrary host

**Severity: Medium**

When preflight is enabled, the follow-up artifact request takes its destination from the server-supplied `Location` header and re-attaches the bearer token when the server says authorization is allowed:

- `crates/turborepo-api-client/src/lib.rs:1075-1099` — `Location` is accepted and parsed with no host allowlist.
- `crates/turborepo-api-client/src/lib.rs:1101-1110` — `allow_auth` is derived from the attacker/server-controlled `Access-Control-Allow-Headers`.
- `crates/turborepo-api-client/src/lib.rs:436-446` — the credential is attached to the redirected URL.

Destination pinning only applies to credentials classified as `saved_vercel`:

- `crates/turborepo-api-client/src/lib.rs:107-112` — `validate_credential_destination` rejects non-approved hosts only for `is_saved_vercel()`.
- `crates/turborepo-api-client/src/lib.rs:58-64` — the no-redirect transport is likewise selected only for `saved_vercel` credentials.

For self-hosted remote caches, a malicious or compromised cache endpoint can answer the preflight with `Location: https://attacker.example/...` and `Access-Control-Allow-Headers: Authorization`, causing the CLI to send the user's cache credential to a third-party origin.

**Recommendation:** Apply an origin allowlist to the post-preflight `Location` (require same origin as `base_url`, or an explicitly configured artifact host) and only forward credentials to that allowlisted origin. Consider treating any cross-origin `Location` as an error.

---

## Risk 3 — Server-supplied verification URI is opened without scheme/origin validation

**Severity: Low**

Device-flow metadata validation covers the four OAuth endpoints but not the verification URIs returned by the device-authorization response, and the CLI opens that URI directly:

- `crates/turborepo-auth/src/device_flow.rs:140-171` — `validate_endpoint_origins` validates only `device_authorization_endpoint`, `token_endpoint`, `revocation_endpoint`, and `introspection_endpoint`.
- `crates/turborepo-auth/src/device_flow.rs:38-52` — `verification_uri` / `verification_uri_complete` are deserialized with no validation.
- `crates/turborepo-auth/src/auth/login.rs:315-333` — the unvalidated URL is passed to `webbrowser::open(verification_url)`.

A compromised or misconfigured auth server could return a non-HTTPS or custom-scheme URI (for example `file:` or an application protocol handler), causing the host OS to launch a local handler. The trust boundary is the auth server plus its TLS, so this is defense-in-depth rather than a direct remote vector, hence Low.

**Recommendation:** Before opening the browser, require `https:` and validate the host against the discovered issuer (same host or an approved subdomain), mirroring the endpoint-origin check.

---

## Notes

- No source files were modified other than adding this report.
- No test suite or build was executed, so none of the above has runtime confirmation.
- `crates/turborepo-auth/src/lib.rs` token persistence uses `create_with_contents_secret` (`crates/turborepo-auth/src/lib.rs:458`, `:472`, `:600`) and has a `0o600` permission assertion (`crates/turborepo-auth/src/lib.rs:1038-1039`); no issue was raised for on-disk credential permissions.
