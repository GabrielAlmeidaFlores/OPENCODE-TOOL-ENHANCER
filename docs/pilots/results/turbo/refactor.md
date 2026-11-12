# Pilot Refactor: `defaultConfigPath` resolution

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** pilot output, structurally verified, not independently reviewed

Scope: one behavior-preserving refactor in `packages/turbo-telemetry/src/utils.ts`.
No source files were modified; this document is the only change.

## Target

`defaultConfigPath` currently reads `process.env.TURBO_CONFIG_DIR_PATH` twice and
mixes a ternary with an `await` inside it:

```ts
async function defaultConfigPath() {
  const dir = process.env.TURBO_CONFIG_DIR_PATH
    ? process.env.TURBO_CONFIG_DIR_PATH
    : await configDir();

  if (!dir) {
    throw new Error("Could not find telemetry config directory");
  }

  return path.join(dir, "turborepo", "telemetry.json");
}
```

## Refactor

Read the environment variable once into a local binding, then branch explicitly.
This removes the duplicate property lookup and the conditional-`await` expression
without changing outcomes.

```ts
async function defaultConfigPath() {
  const envDir = process.env.TURBO_CONFIG_DIR_PATH;
  const dir = envDir ? envDir : await configDir();

  if (!dir) {
    throw new Error("Could not find telemetry config directory");
  }

  return path.join(dir, "turborepo", "telemetry.json");
}
```

## Before / After Plan

1. Before: `defaultConfigPath` evaluates `process.env.TURBO_CONFIG_DIR_PATH` in
   the ternary test and again in the consequent, then conditionally awaits
   `configDir()`.
2. After: the env value is captured once; `configDir()` is still awaited only
   when the captured value is falsy, and the falsy guard plus
   `path.join(dir, "turborepo", "telemetry.json")` remain untouched.
3. Verification (not run here, per instructions): `utils.test.ts` exercises both
   the env-override path and the hash helper, so the existing suite is the
   regression gate; run `pnpm --filter turbo-telemetry test` before merging.

Behavior preservation: the ternary and the single read use identical truthiness
semantics (empty string still falls through to `configDir()`), the `await` is
still lazy, the thrown error message is unchanged, and the returned path is
constructed with the same segments.

## Evidence

- Duplicate env access and conditional `await` are in `defaultConfigPath` at `packages/turbo-telemetry/src/utils.ts:16-18`.
- The falsy-directory guard that must be preserved is at `packages/turbo-telemetry/src/utils.ts:20-22`.
- The env-override expectation that pins this behavior is asserted in `packages/turbo-telemetry/src/utils.test.ts:33-37`.
