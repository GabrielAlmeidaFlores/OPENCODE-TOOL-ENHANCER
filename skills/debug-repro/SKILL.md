---
name: debug-repro
description: Reproduce, minimize, and fix a defect with evidence. Use when behavior is wrong but the cause is unknown.
---

# Debug and Reproduce

## Steps

1. **Reproduce** with the smallest command, input, and environment.
2. **Record** the exact observed and expected behavior.
3. **Minimize** by removing unrelated configuration and data.
4. **Locate** the failure boundary with logs, assertions, or a debugger.
5. **Hypothesize** one cause and design a test that distinguishes it.
6. **Fix** the cause, not the symptom.
7. **Add a regression test** that fails without the fix.

## Rules

- Do not change code before reproducing.
- Do not add logging that includes secrets or personal data.
- Do not "fix" by adding a retry, sleep, or catch-all handler.
- If the bug is intermittent, record timing, concurrency, and ordering.

## Output

Reproduction command, minimized case, root cause, fix, regression test, and residual uncertainty.
