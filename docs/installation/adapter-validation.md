# Real-Repository Adapter Validation: Hono

> **Status:** Experimental · **Last verified:** 2026-11-13 · **Evidence:** deterministic install, update, and uninstall on a pinned clone; Copilot and Codex CLI discovery checks; no model calls

This record validates installation mechanics on a real repository and documents which native clients were checked. It does not measure AI task quality, and it makes no cost or token claim.

## Scope

| Item | Value |
|---|---|
| Repository | `https://github.com/honojs/hono` |
| Commit | `f6fbaf0299c48eea9e656e03e2ffe7ac755e8823` |
| ToolWright version | `0.3.1` source tree |
| Platform | macOS 26.5.2, Python 3.14.7 |
| Profile | `minimal` |
| Adapters | `claude`, `copilot`, `codex` |

## Procedure

```bash
git clone --no-checkout --filter=blob:none https://github.com/honojs/hono /tmp/tw-realrepo-hono/clone
git -C /tmp/tw-realrepo-hono/clone fetch --depth 1 origin f6fbaf0299c48eea9e656e03e2ffe7ac755e8823
git -C /tmp/tw-realrepo-hono/clone checkout --detach FETCH_HEAD
toolwright install --platform claude  --profile minimal --target /tmp/tw-realrepo-hono/clone --apply
toolwright install --platform copilot --profile minimal --target /tmp/tw-realrepo-hono/clone --apply
toolwright install --platform codex   --profile minimal --target /tmp/tw-realrepo-hono/clone --apply
toolwright update --check --target /tmp/tw-realrepo-hono/clone
toolwright uninstall --target /tmp/tw-realrepo-hono/clone --apply --yes
```

## Results

| Adapter | Files written | Reinstall | Update check | Uninstall |
|---|---:|---|---|---|
| `claude` | 48 | 0 new, 0 updated, 48 unchanged | up to date | removed all managed files |
| `copilot` | 49 | not rerun for this adapter | up to date after the Claude run | exit 0 |
| `codex` | 13 | not rerun for this adapter | up to date after the Claude run | exit 0 after the fix |

Additional observations:

- Each adapter generated its native files without creating `.opencode/`.
- The lock reported schema `2`, one active adapter entry per install, and adapter-tagged file entries.
- After uninstall, no managed files remained and the lock contained no file or adapter entries.

## Defect found and fixed

Installing `copilot` and then `codex` produced two lock entries for the shared [`AGENTS.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/AGENTS.md) path. Uninstall attempted to delete the path twice, failed on the second removal, and left stale lock entries.

The fix:

- deduplicates removable paths before unlinking;
- prunes lock entries for removed and missing files after a successful uninstall;
- drops adapter entries that no longer own files.

Regression coverage: `PlatformAdapterInstallTests.test_uninstall_removes_shared_files_across_adapters` and `PlatformAdapterInstallTests.test_uninstall_prunes_entries_for_missing_files`.

## Native discovery checks

The generated files were inspected with the available platform CLIs. No model call was needed. The optional script reproduces the Copilot and Codex checks and skips cleanly when a CLI is absent:

```bash
./scripts/validation/check_adapter_discovery.sh
```

| Client | Version | Command | Result |
|---|---|---|---|
| GitHub Copilot CLI | `1.0.105` | `copilot instruction list` | Found `.github/copilot-instructions.md` and all 12 `.github/instructions/*.instructions.md` files |
| GitHub Copilot CLI | `1.0.105` | `copilot skill list` | Found all 10 generated project skills |
| OpenAI Codex CLI | `0.146.0` | `codex debug prompt-input "Summarize the repository instructions."` | Resolved prompt input contained the generated [`AGENTS.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/AGENTS.md) rules |
| Claude Code CLI | `2.1.323` | `claude doctor` | Exit 0, no installation issues; the CLI has no non-interactive command that lists project agents, commands, or skills, so discovery is unverified |

Observed limits:

- Copilot did not list [`AGENTS.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/AGENTS.md) while `.github/copilot-instructions.md` was present, although the adapter writes both.
- Copilot CLI has no command that lists `.github/prompts/`; prompt-file discovery remains unverified.
- Codex has no non-interactive command that lists custom agents. The TOML files define the required `name`, `description`, and `developer_instructions` fields, but discovery needs an interactive `/agent` session or a model call.
- Codex read-only roles include `sandbox_mode = "read-only"`; write-capable roles omit it and inherit the parent sandbox.
- Claude Code has no non-interactive command that lists project agents, commands, or skills. `claude doctor` verifies the installation but not discovery, which needs an interactive session or a model call.

## Not measured

| Metric | Reason |
|---|---|
| Input and output tokens | No model call was executed. |
| API cost | No model call was executed. |
| Task correctness | No code-change task was executed. |
| Rework and human interventions | No agent workflow was executed. |

Those metrics require the funded pilot runner with `OPENCODE_PILOT_MODEL`. Do not treat this record as a benchmark result.

## References

- [`docs/pilots/README.md`](../pilots/README.md)
- [`docs/benchmarks/methodology.md`](../benchmarks/methodology.md)
- [`docs/installation/toolwright-cli.md`](toolwright-cli.md)
