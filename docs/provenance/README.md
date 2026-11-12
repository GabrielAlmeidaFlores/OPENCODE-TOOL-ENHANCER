# Provenance

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

This directory implements **AGENTS.md Section 2A**: no reusable artifact is authored from scratch when a maintained upstream exists.

## Sources and authors

All sources are pinned to a commit. Versions were retrieved on **2026-11-11**. **No skill or agent in this repository is original work**; each is adapted from the public repositories below.

| ID | Repository | Author | Commit | License |
| --- | --- | --- | --- | --- |
| `volt` | https://github.com/VoltAgent/awesome-claude-code-subagents | VoltAgent | `ed74d115b7fb7026a22a4f816a8e3250f425e3b4` | MIT |
| `wshobson` | https://github.com/wshobson/agents | Seth Hobson (`seth@major7apps.com`) | `9c61ab243def98f72da12abd41cfcf5bcd91af9d` | MIT |
| `superpowers` | https://github.com/obra/superpowers | Jesse Vincent (`jesse@fsck.com`) | `22f0b463e7a5e579904dd6211a520321035526f7` | MIT |
| `ralph` | https://github.com/mikeyobrien/ralph-orchestrator | Ralph Orchestrator Contributors | `64040fd0cda4d83386e4d1d1aa65571dadfe00b3` | MIT |

Every artifact records its author in three places:

1. The skill's `metadata.author`, `metadata.author_url`, and `metadata.author_email` (when published).
2. The agent, command, or hat header (`# author:`, `# author_url:`, `# author_email:`).
3. The `author` and `author_url` fields in `registry.yml`.

`wshobson/agents` is the primary consolidated source: it explicitly supports OpenCode, publishes an OpenCode adapter, and contains 202 agents, 185 skills, and 105 commands. `VoltAgent` supplies the generic role agents that `wshobson` does not publish under the required names. `superpowers` supplies the methodology skills. Ralph supplies its own official presets.

## Registry

`registry.yml` is the source of truth. Every artifact entry records:

- local path
- author, author URL, and email when published
- source repository
- exact upstream path
- upstream commit
- license
- retrieval date
- modification summary

`original_artifacts` records the only permitted local work: configuration composition, glue scripts, test/benchmark fixtures, and project documentation. Each entry states why no upstream artifact applies.

| ID | Kind | Scope |
|---|---|---|
| `benchmark-harness` | fixture | Measurement harness and task definitions |
| `installation-and-validation` | glue | Installer, validator, CI workflows |
| `examples` | fixture | Deliberately defective TypeScript and C# examples |
| `opencode-config` | configuration-composition | V2 options only |
| `project-logo` | original-artwork | Logo variants |
| `ralph-isolated-runner` | glue | Separate-clone runner for Ralph auto-commit |
| `cost-report` | glue | Session artifact aggregation |
| `repository-tests` | fixture | Unit and integration tests, broken fixtures, build entry points |
| `project-documentation` | original-documentation | ADRs, research, guides, and operating docs |
| `memory-and-specs` | glue | Memory store and spec validator; original implementation |
| `verification-and-governance` | glue | Verification engine and governance evaluator; original implementation |
| `catalog-and-profiles` | glue | Catalog generator and profile loader; original implementation |
| `ote-cli` | glue | CLI wrapper over the existing scripts; original implementation |

## Artifact mapping

| Local | Upstream | Modification |
| --- | --- | --- |
| `agents/coordinator` | `wshobson/plugins/agent-teams/agents/team-lead.md` | OpenCode frontmatter, permissions, local harness note |
| `agents/planner` | `volt/categories/08-business-product/project-manager.md` | OpenCode frontmatter, planning focus note |
| `agents/researcher` | `volt/categories/10-research-analysis/research-analyst.md` | OpenCode frontmatter, evidence rules |
| `agents/architect` | `wshobson/plugins/comprehensive-review/agents/architect-review.md` | OpenCode frontmatter |
| `agents/backend-developer` | `volt/categories/01-core-development/backend-developer.md` | OpenCode frontmatter |
| `agents/frontend-developer` | `volt/categories/01-core-development/frontend-developer.md` | OpenCode frontmatter |
| `agents/database-specialist` | `wshobson/plugins/database-design/agents/database-architect.md` | OpenCode frontmatter |
| `agents/code-reviewer` | `volt/categories/04-quality-security/code-reviewer.md` | OpenCode frontmatter |
| `agents/test-engineer` | `volt/categories/04-quality-security/test-automator.md` | OpenCode frontmatter |
| `agents/security-reviewer` | `volt/categories/04-quality-security/security-auditor.md` | OpenCode frontmatter |
| `agents/performance-analyst` | `volt/categories/04-quality-security/performance-engineer.md` | OpenCode frontmatter |
| `agents/documentation-engineer` | `volt/categories/06-developer-experience/documentation-engineer.md` | OpenCode frontmatter |
| `skills/*` | see `registry.yml` | metadata only; three supporting assets normalized to the comment policy |
| `commands/*` | see `registry.yml` | OpenCode frontmatter |
| `configs/ralph/hats/*` | Ralph `presets/*.yml` | extracted hats + per-hat OpenCode backend |

## Updating an artifact

1. Fetch the upstream repository at the recorded commit.
2. Compare the upstream file with the local copy.
3. Apply the smallest possible diff.
4. Update the commit, retrieval date, and modification note in both the file header and `registry.yml`.
5. Run `./scripts/validation/validate.sh`.
6. Reinstall into a clean project and run `opencode debug agents` and the relevant Ralph preflight.

## Adding a new artifact

1. Search the sources above, then other maintained collections.
2. If a suitable upstream exists, copy it and record provenance. Do not write a new one.
3. If no upstream exists, add an `original_artifacts` entry with a justification and obtain human approval.
4. Never add an agent, skill, command, or hat without provenance; the validator fails.

## Removed artifacts

The initial repository contained ten locally authored skills and four locally authored hat collections. They were replaced as follows:

- Skills: replaced by `superpowers` and `wshobson` skills.
- Hats: replaced by Ralph's official `code-assist`, `review`, `research`, and `debug` presets, with only backend routing added.
- Commands: replaced by `wshobson` commands.
- Agents: replaced by `VoltAgent` and `wshobson` agents.

No locally invented agent, skill, command, or hat remains.

## Verification

```bash
./scripts/validation/validate.sh
```

The validator checks that every registered local path exists and that every agent, skill, command, and hat carries provenance metadata.

## License notices

See [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).
