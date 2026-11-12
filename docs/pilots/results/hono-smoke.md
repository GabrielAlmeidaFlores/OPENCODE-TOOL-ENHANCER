# Hono Pilot Smoke

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** verified locally; this is not a pilot result

This run proves the pilot runner executes end to end against a real repository. It is **not** one of the five planned pilot tasks and must not be used as a cost or quality result.

## Run

| Field | Value |
|---|---|
| Repository | `https://github.com/honojs/hono` |
| Commit | `f6fbaf0299c48eea9e656e03e2ffe7ac755e8823` |
| Profile | `minimal` |
| Model | `opencode/deepseek-v4.1-flash-free` |
| Started | 2026-11-12T17:59:26Z |
| Finished | 2026-11-12T17:59:39Z |
| Wall time | 12.53 s |
| OpenCode exit | 0 |
| Verification exit | 0 |
| Input tokens | 9839 |
| Output tokens | 228 |
| Tool calls | 2 |
| Tool errors | 0 |
| Cost | $0.000000 (free model) |

## Prompt

```text
Create a file named PILOT_SMOKE at the repository root containing exactly: ok. Do not modify any other file.
```

## Verification

```bash
test -f PILOT_SMOKE && grep -qx ok PILOT_SMOKE
```

## Limitations

- One smoke task, not the five-task pilot procedure.
- Free model; cost is zero and says nothing about paid-model economics.
- The disposable clone and artifacts were temporary and are not committed.
- No independent reviewer examined the diff.

## Defect found

The first two attempts failed with `Agent not found: "coordinator"`. The runner passed `cwd` but inherited `PWD` from the parent, so OpenCode resolved the project from the wrong directory. The runner now sets `PWD` and `OPENCODE_CONFIG` for the clone, and the regression is covered by the mocked end-to-end test.

## References

- `docs/pilots/README.md`
- `packages/ote_cli/ote_cli/pilot.py`
