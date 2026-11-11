---
name: security-review
description: Review a change for exploitable vulnerabilities. Use before merging auth, input handling, file, network, or dependency changes.
---

# Security Review

## Checklist

1. **Input** — validation, encoding, length, type confusion at every boundary.
2. **AuthN/AuthZ** — object-level checks, role escalation, tenant isolation.
3. **Injection** — SQL, shell, template, header, log, path traversal.
4. **Secrets** — committed keys, tokens in logs, weak randomness.
5. **Dependencies** — new packages, known CVEs, typosquatting, license.
6. **Exposure** — verbose errors, debug routes, PII in telemetry.
7. **SSRF** — allowlists, redirects, metadata endpoints.
8. **Files** — upload type checks, storage paths, archive extraction.
9. **Crypto** — algorithm, key management, constant-time comparison.

## Output

Severity, `file:line`, exploit scenario, impact, remediation, and the assumption required for exploitability.

## Rules

- Do not test against systems you do not own.
- Do not paste real secrets.
- Verify framework defaults; do not assume they are safe.
