# OPENCODE-TOOL-ENHANCER

A reproducible, cost-aware configuration for [OpenCode](https://opencode.ai) with a custom primary agent, specialized subagents, Ralph Orchestrator, and a maximal code-intelligence stack (ripgrep, ast-grep, Serena, CodeGraph).

This repository is configuration and documentation, not a fork of OpenCode. It is designed to be read, copied, and validated.

## Status

| Area | State |
| --- | --- |
| Research and decisions | Complete (Phase 1) |
| OpenCode configuration | V2 native (`2.2.7`), validated against the published schema |
| Orchestration | Ralph Orchestrator `2.10.1` (primary) + OpenCode-native fallback |
| Default toolset | native tools, ripgrep, ast-grep, Serena MCP, CodeGraph MCP |
| Benchmarks | Methodology and harness only; no published results yet |

> **Important compatibility note.** The project targets OpenCode **V2** (`2.2.x`). V2 reads V1 configuration, but V2 **does not run language servers** or expose LSP tools. Serena replaces native LSP for symbol-level navigation. See [ADR-001](docs/decisions/ADR-001-opencode-v2-baseline.md).

## What you get

- A **custom primary agent** (`coordinator`) that plans, delegates, and enforces verification instead of using the default Build agent.
- **Eleven specialized subagents** with least-privilege permissions and explicit delegation rules.
- **Ralph Orchestrator** hat collections with backpressure gates (tests, lint, typecheck) and persistent memories/tasks.
- A **skills pack** for common code-development workflows.
- **Code-intelligence defaults** with MCP overhead controls (Code Mode, denied tools, on-demand servers).
- Installation, validation, benchmarking, and rollback scripts that never silently modify your configuration.

## Quick start

### 1. Prerequisites

- macOS or Linux (Windows is best-effort; see [troubleshooting](docs/troubleshooting/README.md)).
- `git`, `node` >= 20, `python3`, `ripgrep` (`rg`).
- An OpenCode provider credential. Models are referenced as `provider/model#variant`; nothing is hardcoded.

### 2. Inspect before installing

```bash
git clone <your-fork-url> OPENCODE-TOOL-ENHANCER
cd OPENCODE-TOOL-ENHANCER
./scripts/installation/install.sh --check
./scripts/installation/install.sh --dry-run --all
```

### 3. Apply (explicit opt-in)

```bash
./scripts/installation/install.sh --apply --only opencode
```

The installer backs up existing files and prints a rollback command. It writes only to the target project and never edits `~/.config/opencode`.

### 4. Copy the project configuration

```bash
mkdir -p .opencode/agents .opencode/commands .opencode/skills
cp configs/opencode/opencode.jsonc .opencode/opencode.jsonc

for f in agents/*/AGENT.md; do
  role=$(basename "$(dirname "$f")")
  cp "$f" ".opencode/agents/$role.md"
done

cp commands/*.md .opencode/commands/
for d in skills/*/; do
  name=$(basename "$d")
  mkdir -p ".opencode/skills/$name"
  cp "$d/SKILL.md" ".opencode/skills/$name/SKILL.md"
done
```

### 5. Verify

```bash
opencode --version            # expect 2.2.x
opencode debug config      # configuration sources
opencode debug agents      # agent discovery
opencode mcp list
./scripts/validation/validate.sh
```

Then start OpenCode and select the `coordinator` agent.

## Repository map

```text
.
├── README.md
├── AGENTS.md                     # project brief (source requirements)
├── docs/
│   ├── decisions/                # architecture decision records
│   ├── research/                 # evidence, compatibility, comparisons
│   ├── installation/             # per-component install guides
│   ├── configuration/            # OpenCode V2 reference
│   ├── orchestration/            # Ralph workflows and gates
│   ├── agents/                   # roles and delegation policy
│   ├── code-intelligence/        # ast-grep, Serena, CodeGraph, ripgrep
│   ├── cost-optimization/
│   ├── benchmarks/
│   └── troubleshooting/
├── configs/
│   ├── opencode/                 # V2 config profiles
│   └── ralph/                    # core config + hat collections
├── agents/<role>/AGENT.md        # canonical agent instructions
├── skills/<name>/SKILL.md        # installable skills
├── scripts/                      # installation, validation, benchmarking, maintenance
├── examples/                     # TypeScript, C#, multi-agent
└── benchmarks/                   # methodology, tasks, harness, results
```

## Core principles

1. **Quality first.** Token savings do not count if correctness or rework gets worse.
2. **Deterministic tools first.** Tests, linters, type checkers, and AST queries run without model tokens.
3. **Minimal context by default.** MCP servers are added only with a documented reason and an overhead control.
4. **No hardcoded models.** Routing is configuration, not source code.
5. **Human approval for destructive operations.** Installers default to check/dry-run.

## Documentation

- [Phase 1 research report](docs/research/phase1-research-report.md)
- [Compatibility matrix](docs/research/compatibility-matrix.md)
- [Architecture overview](docs/architecture/overview.md)
- [OpenCode V2 configuration](docs/configuration/opencode-v2.md)
- [Agent roles and delegation](docs/agents/roles.md)
- [Ralph orchestration](docs/orchestration/ralph.md)
- [Code intelligence](docs/code-intelligence/README.md)
- [Cost optimization](docs/cost-optimization/README.md)
- [Benchmark methodology](docs/benchmarks/methodology.md)
- [Validation checklist](docs/validation-checklist.md)

## License

Repository content is MIT. Third-party tools keep their own licenses; see [ADR-003](docs/decisions/ADR-003-maximal-code-intelligence.md) and the per-tool pages. Serena is GPL-3.0-or-later; it is installed as an external tool and is not vendored here.
