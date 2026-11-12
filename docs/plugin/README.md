# Opt-in Memory Plugin

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** plugin file syntax-checked and install plan tested; runtime hook not executed in CI

This OpenCode V2 plugin injects the bounded memory preamble at the start of each model request. It is disabled by default and performs no network access or telemetry.

## What it does

1. Checks for `.ote/memory/plugin.enabled`.
2. Runs `ote memory preamble --budget 1200` in the project directory.
3. Pushes the result into the session `context` hook as a system text block.
4. Caches the preamble per session.

If `ote` is missing, the sentinel is absent, or the command fails, the plugin does nothing.

## Install

Install the plugin file explicitly:

```bash
ote install --only plugin --target /path/to/project --apply
```

Or install the `full` profile, which includes the plugin but leaves it inactive.

Enable it in the project:

```bash
touch /path/to/project/.ote/memory/plugin.enabled
```

The plugin is discovered from `.opencode/plugins/ote-memory.js`. Restart the OpenCode service after adding it:

```bash
opencode service restart
```

## Verify

```bash
opencode plugin list
```

Look for `ote.memory`. A session then receives the preamble; `/context` or the model request shows the injected block.

## Disable

```bash
rm /path/to/project/.ote/memory/plugin.enabled
```

Remove the plugin file entirely with `ote uninstall` or by deleting `.opencode/plugins/ote-memory.js`.

## Requirements

- OpenCode V2 plugin API (`@opencode/plugin`).
- `ote` available on `PATH` in the OpenCode server environment.
- Python 3.11+ and a valid `.ote/memory` directory.

## Limitations

- No TUI, GUI, or telemetry; it only injects memory.
- Plugin API is experimental and may change between OpenCode releases.
- Failures are silent by design so an unavailable CLI cannot break a session.
- The sentinel is per project; there is no global toggle.
- The preamble budget is 1200 tokens in the plugin, independent of the CLI default.

## Design reference

The session `context` hook pattern follows `aerovato/operator-memory`'s OpenCode V2 adapter (BSD-3-Clause); the opt-in plugin structure follows `DVNghiem/FlowDeck` (MIT). The implementation is original JavaScript; see the `task-board-and-plugin` entry in `docs/provenance/registry.yml`.

## References

- `docs/memory/README.md`
- `docs/cli/README.md`
- https://opencode.ai/docs/build/plugins/
